import torch
from torch import einsum, nn
from einops import rearrange, repeat
from einops.layers.torch import Rearrange
from efficientnet_pytorch import EfficientNet


CROSS_EFFICIENT_VIT_CONFIG = {
    "model": {
        "image-size": 224,
        "num-classes": 1,
        "depth": 4,
        "sm-dim": 192,
        "sm-patch-size": 7,
        "sm-enc-depth": 2,
        "sm-enc-dim-head": 64,
        "sm-enc-heads": 8,
        "sm-enc-mlp-dim": 2048,
        "lg-dim": 384,
        "lg-patch-size": 56,
        "lg-enc-depth": 3,
        "lg-enc-dim-head": 64,
        "lg-enc-heads": 8,
        "lg-enc-mlp-dim": 2048,
        "cross-attn-depth": 2,
        "cross-attn-dim-head": 64,
        "cross-attn-heads": 8,
        "lg-channels": 24,
        "sm-channels": 1280,
        "dropout": 0.15,
        "emb-dropout": 0.15,
    }
}


def default(value, fallback):
    return value if value is not None else fallback


class EfficientNetBackbone(EfficientNet):
    def delete_blocks(self, limit):
        pass

    def extract_features_at_block(self, inputs, selected_block):
        x = self._swish(self._bn0(self._conv_stem(inputs)))

        for idx, block in enumerate(self._blocks):
            drop_connect_rate = self._global_params.drop_connect_rate
            if drop_connect_rate:
                drop_connect_rate *= float(idx) / len(self._blocks)
            x = block(x, drop_connect_rate=drop_connect_rate)

            if idx > selected_block:
                break

        if selected_block >= len(self._blocks):
            x = self._swish(self._bn1(self._conv_head(x)))

        return x


class PreNorm(nn.Module):
    def __init__(self, dim, fn):
        super().__init__()
        self.norm = nn.LayerNorm(dim)
        self.fn = fn

    def forward(self, x, **kwargs):
        return self.fn(self.norm(x), **kwargs)


class FeedForward(nn.Module):
    def __init__(self, dim, hidden_dim, dropout=0.0):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, dim),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


class Attention(nn.Module):
    def __init__(self, dim, heads=8, dim_head=64, dropout=0.0):
        super().__init__()
        inner_dim = dim_head * heads
        self.heads = heads
        self.scale = dim_head**-0.5
        self.attend = nn.Softmax(dim=-1)
        self.to_q = nn.Linear(dim, inner_dim, bias=False)
        self.to_kv = nn.Linear(dim, inner_dim * 2, bias=False)
        self.to_out = nn.Sequential(nn.Linear(inner_dim, dim), nn.Dropout(dropout))

    def forward(self, x, context=None, kv_include_self=False):
        _, _, _, heads = *x.shape, self.heads
        context = default(context, x)

        if kv_include_self:
            context = torch.cat((x, context), dim=1)

        qkv = (self.to_q(x), *self.to_kv(context).chunk(2, dim=-1))
        q, k, v = map(lambda t: rearrange(t, "b n (h d) -> b h n d", h=heads), qkv)
        dots = einsum("b h i d, b h j d -> b h i j", q, k) * self.scale
        attn = self.attend(dots)
        out = einsum("b h i j, b h j d -> b h i d", attn, v)
        out = rearrange(out, "b h n d -> b n (h d)")
        return self.to_out(out)


class Transformer(nn.Module):
    def __init__(self, dim, depth, heads, dim_head, mlp_dim, dropout=0.0):
        super().__init__()
        self.layers = nn.ModuleList([])
        self.norm = nn.LayerNorm(dim)
        for _ in range(depth):
            self.layers.append(
                nn.ModuleList(
                    [
                        PreNorm(
                            dim,
                            Attention(
                                dim, heads=heads, dim_head=dim_head, dropout=dropout
                            ),
                        ),
                        PreNorm(dim, FeedForward(dim, mlp_dim, dropout=dropout)),
                    ]
                )
            )

    def forward(self, x):
        for attn, ff in self.layers:
            x = attn(x) + x
            x = ff(x) + x
        return self.norm(x)


class ProjectInOut(nn.Module):
    def __init__(self, dim_in, dim_out, fn):
        super().__init__()
        self.fn = fn
        need_projection = dim_in != dim_out
        self.project_in = nn.Linear(dim_in, dim_out) if need_projection else nn.Identity()
        self.project_out = nn.Linear(dim_out, dim_in) if need_projection else nn.Identity()

    def forward(self, x, *args, **kwargs):
        x = self.project_in(x)
        x = self.fn(x, *args, **kwargs)
        return self.project_out(x)


class CrossTransformer(nn.Module):
    def __init__(self, sm_dim, lg_dim, depth, heads, dim_head, dropout):
        super().__init__()
        self.layers = nn.ModuleList([])
        for _ in range(depth):
            self.layers.append(
                nn.ModuleList(
                    [
                        ProjectInOut(
                            sm_dim,
                            lg_dim,
                            PreNorm(
                                lg_dim,
                                Attention(
                                    lg_dim,
                                    heads=heads,
                                    dim_head=dim_head,
                                    dropout=dropout,
                                ),
                            ),
                        ),
                        ProjectInOut(
                            lg_dim,
                            sm_dim,
                            PreNorm(
                                sm_dim,
                                Attention(
                                    sm_dim,
                                    heads=heads,
                                    dim_head=dim_head,
                                    dropout=dropout,
                                ),
                            ),
                        ),
                    ]
                )
            )

    def forward(self, sm_tokens, lg_tokens):
        (sm_cls, sm_patch_tokens), (lg_cls, lg_patch_tokens) = map(
            lambda t: (t[:, :1], t[:, 1:]), (sm_tokens, lg_tokens)
        )

        for sm_attend_lg, lg_attend_sm in self.layers:
            sm_cls = (
                sm_attend_lg(sm_cls, context=lg_patch_tokens, kv_include_self=True)
                + sm_cls
            )
            lg_cls = (
                lg_attend_sm(lg_cls, context=sm_patch_tokens, kv_include_self=True)
                + lg_cls
            )

        return torch.cat((sm_cls, sm_patch_tokens), dim=1), torch.cat(
            (lg_cls, lg_patch_tokens), dim=1
        )


class MultiScaleEncoder(nn.Module):
    def __init__(
        self,
        *,
        depth,
        sm_dim,
        lg_dim,
        sm_enc_params,
        lg_enc_params,
        cross_attn_heads,
        cross_attn_depth,
        cross_attn_dim_head=64,
        dropout=0.0
    ):
        super().__init__()
        self.layers = nn.ModuleList([])
        for _ in range(depth):
            self.layers.append(
                nn.ModuleList(
                    [
                        Transformer(dim=sm_dim, dropout=dropout, **sm_enc_params),
                        Transformer(dim=lg_dim, dropout=dropout, **lg_enc_params),
                        CrossTransformer(
                            sm_dim=sm_dim,
                            lg_dim=lg_dim,
                            depth=cross_attn_depth,
                            heads=cross_attn_heads,
                            dim_head=cross_attn_dim_head,
                            dropout=dropout,
                        ),
                    ]
                )
            )

    def forward(self, sm_tokens, lg_tokens):
        for sm_enc, lg_enc, cross_attend in self.layers:
            sm_tokens, lg_tokens = sm_enc(sm_tokens), lg_enc(lg_tokens)
            sm_tokens, lg_tokens = cross_attend(sm_tokens, lg_tokens)

        return sm_tokens, lg_tokens


class ImageEmbedder(nn.Module):
    def __init__(
        self,
        *,
        dim,
        image_size,
        patch_size,
        dropout=0.0,
        efficient_block=8,
        channels
    ):
        super().__init__()
        self.efficient_net = EfficientNetBackbone.from_name("efficientnet-b0")
        self.efficient_net.delete_blocks(efficient_block)
        self.efficient_block = efficient_block
        num_patches = (image_size // patch_size) ** 2
        patch_dim = channels * patch_size**2
        self.to_patch_embedding = nn.Sequential(
            Rearrange(
                "b c (h p1) (w p2) -> b (h w) (p1 p2 c)",
                p1=patch_size,
                p2=patch_size,
            ),
            nn.Linear(patch_dim, dim),
        )
        self.pos_embedding = nn.Parameter(torch.randn(1, num_patches + 1, dim))
        self.cls_token = nn.Parameter(torch.randn(1, 1, dim))
        self.dropout = nn.Dropout(dropout)

    def forward(self, img):
        x = self.efficient_net.extract_features_at_block(img, self.efficient_block)
        x = self.to_patch_embedding(x)
        batch_size, num_tokens, _ = x.shape
        cls_tokens = repeat(self.cls_token, "() n d -> b n d", b=batch_size)
        x = torch.cat((cls_tokens, x), dim=1)
        x += self.pos_embedding[:, : num_tokens + 1]
        return self.dropout(x)


class CrossEfficientViT(nn.Module):
    def __init__(self, *, config=CROSS_EFFICIENT_VIT_CONFIG):
        super().__init__()
        model_config = config["model"]
        image_size = model_config["image-size"]
        num_classes = model_config["num-classes"]
        sm_dim = model_config["sm-dim"]
        sm_channels = model_config["sm-channels"]
        lg_dim = model_config["lg-dim"]
        lg_channels = model_config["lg-channels"]
        sm_patch_size = model_config["sm-patch-size"]
        lg_patch_size = model_config["lg-patch-size"]

        self.sm_image_embedder = ImageEmbedder(
            dim=sm_dim,
            image_size=image_size,
            patch_size=sm_patch_size,
            dropout=model_config["emb-dropout"],
            efficient_block=16,
            channels=sm_channels,
        )
        self.lg_image_embedder = ImageEmbedder(
            dim=lg_dim,
            image_size=image_size,
            patch_size=lg_patch_size,
            dropout=model_config["emb-dropout"],
            efficient_block=1,
            channels=lg_channels,
        )
        self.multi_scale_encoder = MultiScaleEncoder(
            depth=model_config["depth"],
            sm_dim=sm_dim,
            lg_dim=lg_dim,
            cross_attn_heads=model_config["cross-attn-heads"],
            cross_attn_dim_head=model_config["cross-attn-dim-head"],
            cross_attn_depth=model_config["cross-attn-depth"],
            sm_enc_params={
                "depth": model_config["sm-enc-depth"],
                "heads": model_config["sm-enc-heads"],
                "mlp_dim": model_config["sm-enc-mlp-dim"],
                "dim_head": model_config["sm-enc-dim-head"],
            },
            lg_enc_params={
                "depth": model_config["lg-enc-depth"],
                "heads": model_config["lg-enc-heads"],
                "mlp_dim": model_config["lg-enc-mlp-dim"],
                "dim_head": model_config["lg-enc-dim-head"],
            },
            dropout=model_config["dropout"],
        )
        self.sm_mlp_head = nn.Sequential(nn.LayerNorm(sm_dim), nn.Linear(sm_dim, num_classes))
        self.lg_mlp_head = nn.Sequential(nn.LayerNorm(lg_dim), nn.Linear(lg_dim, num_classes))

    def forward(self, img):
        sm_tokens = self.sm_image_embedder(img)
        lg_tokens = self.lg_image_embedder(img)
        sm_tokens, lg_tokens = self.multi_scale_encoder(sm_tokens, lg_tokens)
        sm_cls, lg_cls = map(lambda t: t[:, 0], (sm_tokens, lg_tokens))
        return self.sm_mlp_head(sm_cls) + self.lg_mlp_head(lg_cls)

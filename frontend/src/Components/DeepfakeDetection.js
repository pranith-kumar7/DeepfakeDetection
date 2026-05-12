import React, { useMemo, useState } from 'react';
import axios from 'axios';
import { Bar, Line, Radar } from 'react-chartjs-2';
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  RadialLinearScale,
  Title,
  Tooltip,
} from 'chart.js';
import { Link, useOutletContext } from 'react-router-dom';

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  Filler,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  RadialLinearScale
);

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

function DeepfakeDetection() {
  const { currentUser } = useOutletContext();
  const [file, setFile] = useState(null);
  const [type, setType] = useState('image');
  const [result, setResult] = useState('');
  const [confidence, setConfidence] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filePreview, setFilePreview] = useState(null);
  const [analysisDetails, setAnalysisDetails] = useState({});
  const [insight, setInsight] = useState(null);
  const [performanceData, setPerformanceData] = useState([]);
  const [frameScores, setFrameScores] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) {
      return;
    }

    setFile(selectedFile);
    setResult('');
    setConfidence(null);
    setFilePreview(URL.createObjectURL(selectedFile));
    setPerformanceData([]);
    setFrameScores([]);
    setAnalysisDetails({});
    setInsight(null);
    setErrorMessage('');
  };

  const handleSubmit = async () => {
    if (!currentUser) {
      setErrorMessage('Please sign in before running a detection.');
      return;
    }

    if (!file) {
      setErrorMessage('Please upload a file first.');
      return;
    }

    setLoading(true);
    setErrorMessage('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const endpoint = type === 'image' ? '/predict' : '/predict-video';
      const response = await axios.post(`${API_BASE_URL}${endpoint}`, formData);
      const data = response.data;
      const nextResult = data.result || '';
      const nextConfidence = data.confidence ?? 0;

      setResult(nextResult);
      setConfidence(nextConfidence);
      setAnalysisDetails({
        fakeScore: data.fake_score,
        realScore: data.real_score,
        rawProbability: data.raw_probability,
        framesAnalyzed: data.frames_processed,
      });
      setInsight(data.insight || null);
      setPerformanceData(data.performance || []);
      setFrameScores(data.frame_scores || []);
    } catch (requestError) {
      console.error('Prediction error:', requestError);
      setErrorMessage(
        requestError.response?.data?.error ||
          'Prediction failed. Make sure the backend server is running.'
      );
      setResult('');
      setConfidence(null);
      setPerformanceData([]);
      setFrameScores([]);
      setAnalysisDetails({});
      setInsight(null);
    } finally {
      setLoading(false);
    }
  };

  const derivedScores = useMemo(() => {
    if (analysisDetails.fakeScore !== undefined && analysisDetails.realScore !== undefined) {
      return {
        fake: Number(analysisDetails.fakeScore),
        real: Number(analysisDetails.realScore),
      };
    }

    if (typeof analysisDetails.rawProbability === 'number') {
      const raw = analysisDetails.rawProbability * 100;
      return result === 'REAL'
        ? { fake: 100 - raw, real: raw }
        : { fake: raw, real: 100 - raw };
    }

    if (confidence !== null && result === 'FAKE') {
      return { fake: confidence, real: 100 - confidence };
    }

    if (confidence !== null && result === 'REAL') {
      return { fake: 100 - confidence, real: confidence };
    }

    return { fake: null, real: null };
  }, [analysisDetails.fakeScore, analysisDetails.rawProbability, analysisDetails.realScore, confidence, result]);

  const hasPredictionScores = derivedScores.fake !== null && derivedScores.real !== null;
  const fakeScore = hasPredictionScores
    ? Math.max(0, Math.min(100, Number(derivedScores.fake.toFixed(2))))
    : 0;
  const realScore = hasPredictionScores
    ? Math.max(0, Math.min(100, Number(derivedScores.real.toFixed(2))))
    : 0;
  const displayConfidence = hasPredictionScores
    ? Math.max(fakeScore, realScore)
    : confidence ?? 0;
  const insightMetrics = useMemo(() => insight?.metrics || {}, [insight]);

  const scoreBarData = useMemo(
    () => ({
      labels: ['Fake likelihood', 'Real likelihood'],
      datasets: [
        {
          label: 'Prediction score (%)',
          data: [fakeScore, realScore],
          backgroundColor: ['rgba(239, 71, 111, 0.8)', 'rgba(17, 138, 178, 0.8)'],
          borderRadius: 8,
        },
      ],
    }),
    [fakeScore, realScore]
  );

  const radarData = useMemo(
    () => ({
      labels: ['Confidence', 'Score gap', 'Consistency', 'Certainty'],
      datasets: [
        {
          label: 'Analysis strength',
          data: [
            insightMetrics.confidence ?? displayConfidence,
            insightMetrics.score_gap ?? Math.abs(fakeScore - realScore),
            insightMetrics.consistency ?? 100,
            100 - (insightMetrics.uncertainty ?? 100 - displayConfidence),
          ],
          backgroundColor: 'rgba(17, 138, 178, 0.18)',
          borderColor: '#118ab2',
          pointBackgroundColor: '#ef476f',
          borderWidth: 2,
        },
      ],
    }),
    [displayConfidence, fakeScore, insightMetrics, realScore]
  );

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        min: 0,
        max: 100,
      },
    },
  };

  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: {
          stepSize: 25,
        },
      },
    },
  };

  const performanceChartData = useMemo(
    () => ({
      labels: performanceData.map((_, index) => `Frame ${index + 1}`),
      datasets: [
        {
          label: 'Frame confidence (%)',
          data: performanceData,
          borderColor: '#f4a261',
          backgroundColor: 'rgba(244, 162, 97, 0.2)',
          fill: true,
          tension: 0.35,
          pointRadius: 3,
        },
      ],
    }),
    [performanceData]
  );

  return (
    <section className="detector-page">
      <div className="detector-header">
        <div>
          <span className="eyebrow">Analysis workspace</span>
          <h1>Run media through the detection pipeline.</h1>
          <p>
            Review prediction confidence, fake and real likelihood, score gap, uncertainty, and
            frame-level evidence for videos.
          </p>
        </div>
        <div className="status-pill">{currentUser ? `Welcome, ${currentUser.name}` : 'Sign in to continue'}</div>
      </div>

      {!currentUser ? (
        <div className="signin-warning">
          <p>Please sign in before checking a file.</p>
          <Link className="hero-button hero-button--primary" to="/auth">
            Sign In
          </Link>
        </div>
      ) : null}

      <div className="detector-grid">
        <div className="detector-card">
          <label className="field">
            <span>Choose file type</span>
            <select value={type} onChange={(event) => setType(event.target.value)}>
              <option value="image">Image</option>
              <option value="video">Video</option>
            </select>
          </label>

          <label className="upload-box">
            <span>{file ? file.name : `Choose a ${type} file`}</span>
            <input
              type="file"
              accept={type === 'image' ? 'image/*' : 'video/*'}
              onChange={handleFileChange}
            />
          </label>

          {errorMessage ? <div className="form-message form-message--error">{errorMessage}</div> : null}

          <button className="submit-button" type="button" disabled={loading} onClick={handleSubmit}>
            {loading ? 'Analyzing...' : `Analyze ${type}`}
          </button>
        </div>

        <div className="detector-card detector-card--preview">
          <h3>Preview</h3>
          {filePreview ? (
            type === 'image' ? (
              <img className="preview-media" src={filePreview} alt="Preview" />
            ) : (
              <video className="preview-media" controls>
                <source src={filePreview} />
              </video>
            )
          ) : (
            <p className="muted-copy">Selected media preview appears here.</p>
          )}
        </div>
      </div>

      {(result || confidence !== null) && (
        <div className="results-grid">
          <div className="result-card">
            <span className="eyebrow">Result</span>
            <h2>{result}</h2>
            <div className={`confidence-meter confidence-meter--${result.toLowerCase()}`}>
              <strong>{displayConfidence}%</strong>
              <span>prediction confidence</span>
            </div>
            {insight ? <p>{insight.summary}</p> : null}
            {insight?.certainty ? <p>Certainty: {insight.certainty}</p> : null}
            {insight?.risk_level ? <p>Risk level: {insight.risk_level}</p> : null}
            {analysisDetails.framesAnalyzed ? (
              <p>Scenes checked: {analysisDetails.framesAnalyzed}</p>
            ) : null}
            {insight?.frames ? (
              <p>
                Fake-leaning scenes: {insight.frames.fake_leaning} | Real-leaning scenes:{' '}
                {insight.frames.real_leaning}
              </p>
            ) : null}
          </div>

          <div className="result-card">
            <h3>Prediction scores</h3>
            <div className="chart-panel">
              <Bar data={scoreBarData} options={chartOptions} />
            </div>
            <div className="score-bars">
              <div className="score-row">
                <div>
                  <strong>Fake likelihood</strong>
                  <span>{fakeScore}%</span>
                </div>
                <div className="score-track">
                  <div className="score-fill score-fill--fake" style={{ width: `${fakeScore}%` }} />
                </div>
              </div>
              <div className="score-row">
                <div>
                  <strong>Real likelihood</strong>
                  <span>{realScore}%</span>
                </div>
                <div className="score-track">
                  <div className="score-fill score-fill--real" style={{ width: `${realScore}%` }} />
                </div>
              </div>
            </div>
            <p className="muted-copy">
              Confidence is the higher of these two prediction scores.
            </p>
          </div>

          <div className="result-card">
            <h3>Analysis strength</h3>
            <div className="chart-panel">
              <Radar data={radarData} options={radarOptions} />
            </div>
            <div className="metric-grid">
              <div>
                <span>Score gap</span>
                <strong>{insightMetrics.score_gap ?? Math.abs(fakeScore - realScore)}%</strong>
              </div>
              <div>
                <span>Uncertainty</span>
                <strong>{insightMetrics.uncertainty ?? 100 - displayConfidence}%</strong>
              </div>
              <div>
                <span>Consistency</span>
                <strong>{insightMetrics.consistency ?? 100}%</strong>
              </div>
            </div>
          </div>

          {performanceData.length > 0 ? (
            <div className="result-card result-card--wide">
              <h3>Frame analysis</h3>
              <div className="chart-panel chart-panel--wide">
                <Line data={performanceChartData} options={chartOptions} />
              </div>
              {insight?.frames ? (
                <div className="metric-grid metric-grid--video">
                  <div>
                    <span>Average frame confidence</span>
                    <strong>{insight.frames.avg_confidence}%</strong>
                  </div>
                  <div>
                    <span>Lowest frame confidence</span>
                    <strong>{insight.frames.min_confidence}%</strong>
                  </div>
                  <div>
                    <span>Highest frame confidence</span>
                    <strong>{insight.frames.max_confidence}%</strong>
                  </div>
                </div>
              ) : null}
              {frameScores.length > 0 ? (
                <div className="frame-grid">
                  {frameScores.map((frame) => (
                    <div className="frame-chip" key={frame.frame}>
                      <span>Frame {frame.frame}</span>
                      <strong>{frame.result}</strong>
                      <small>{frame.confidence}%</small>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      )}
    </section>
  );
}

export default DeepfakeDetection;

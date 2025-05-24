// frontend/src/components/Webhome.js
import React from 'react';
import { Link } from 'react-router-dom';
import i from '../Assets/image.jpg';
import m from '../Assets/image.jpg';

function Webhome() {
  return (
    <div style={{ position: 'relative' }}>
      <div id="carouselExampleIndicators" className="carousel slide" data-bs-ride="carousel" data-bs-interval="3000">
        {/* Carousel Indicators */}
        <div className="carousel-indicators">
          <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="0" className="active" aria-current="true" aria-label="Slide 1"></button>
          <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="1" aria-label="Slide 2"></button>
          <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="2" aria-label="Slide 3"></button>
        </div>

        {/* Carousel Images */}
        <div className="carousel-inner">
          <div className="carousel-item active">
            <img src={i} className="d-block w-100" alt="First slide" />
          </div>
          <div className="carousel-item">
            <img src={i} className="d-block w-100" alt="Second slide" />
          </div>
          <div className="carousel-item">
            <img src={m} className="d-block w-100" alt="Third slide" />
          </div>
        </div>

        {/* Previous & Next Buttons */}
        <button className="carousel-control-prev" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="prev">
          <span className="carousel-control-prev-icon" aria-hidden="true"></span>
          <span className="visually-hidden">Previous</span>
        </button>
        <button className="carousel-control-next" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="next">
          <span className="carousel-control-next-icon" aria-hidden="true"></span>
          <span className="visually-hidden">Next</span>
        </button>
      </div>

      {/* Text Overlay */}
      <div style={{
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        zIndex: 10,
        backgroundColor: "rgba(0, 0, 0, 0.5)",
        padding: "30px 40px",
        borderRadius: "10px",
        textAlign: "center",
        maxWidth: "800px",
        width: "90%"
      }}>
        {/* Get Started Button */}
        <Link to="/login">
          <button style={{
            backgroundColor: "#007bff",
            color: "#fff",
            padding: "10px 20px",
            border: "none",
            borderRadius: "30px",
            fontSize: "1rem",
            marginBottom: "20px",
            fontWeight: "bold",
            cursor: "pointer",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.3)",
            transition: "background-color 0.3s ease"
          }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#0056b3"}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#007bff"}
          >
            Get Started
          </button>
        </Link>

        <h1 style={{
          color: "#ffffff",
          fontWeight: "bold",
          fontSize: "2.5rem",
          textShadow: "2px 2px 10px rgba(0, 0, 0, 0.8)"
        }}>
          Uncover the Truth Behind Every Frame
        </h1>
        <p style={{
          color: "#f1f1f1",
          fontSize: "1.2rem",
          marginTop: "15px",
          lineHeight: "1.6",
          textShadow: "1px 1px 8px rgba(0, 0, 0, 0.6)"
        }}>
          This platform offers an intuitive and interactive experience for detecting manipulated media. 
          Effortlessly upload content, access detailed analysis, and gain valuable insights — all through a streamlined, secure interface.
        </p>
      </div>
    </div>
  );
}

export default Webhome;

import React, { useState } from 'react';
import axios from 'axios';
import { Pie, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  LineElement,
  BarElement,
  PointElement,
  CategoryScale,
  LinearScale,
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, ArcElement, LineElement, BarElement, PointElement, CategoryScale, LinearScale);

function DeepfakeDetection() {
  const [file, setFile] = useState(null);
  const [type, setType] = useState('');
  const [result, setResult] = useState('');
  const [confidence, setConfidence] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filePreview, setFilePreview] = useState(null);
  const [analysisDetails, setAnalysisDetails] = useState({});
  const [performanceData, setPerformanceData] = useState([]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setResult('');
    setConfidence(null);
    setFilePreview(URL.createObjectURL(selectedFile));
    setPerformanceData([]);
    setAnalysisDetails({});
  };

  const handleSubmit = async () => {
    if (!file) {
      alert("Please upload a file first.");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const endpoint = type === "image" ? "/predict" : "/predict-video";
      const response = await axios.post(`http://localhost:5000${endpoint}`, formData);
      const data = response.data;

      setResult(data.result || '');
      setConfidence(data.confidence || 0);

      if (type === "video" && data.frames_processed) {
        setAnalysisDetails({
          framesAnalyzed: data.frames_processed,
          processingTime: data.processing_time,
          modelConfidence: data.confidence,
          analyzedFrames: data.analyzed_frames,
        });
        setPerformanceData(data.performance || []);
      } else {
        setPerformanceData([]);
        setAnalysisDetails({});
      }

    } catch (error) {
      console.error("Prediction error:", error);
      setResult("Error occurred during prediction.");
      setConfidence(null);
      setPerformanceData([]);
      setAnalysisDetails({});
    }

    setLoading(false);
  };

  const pieData = {
    labels: ['Fake', 'Real'],
    datasets: [
      {
        data: [
          confidence !== null ? 100 - confidence : 50,
          confidence !== null ? confidence : 50,
        ],
        backgroundColor: ['#f44336', '#4caf50'],
      },
    ],
  };

  const performanceChartData = {
    labels: performanceData.map((_, idx) => `Frame ${idx + 1}`),
    datasets: [
      {
        label: 'Confidence per Frame (%)',
        data: performanceData,
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: true,
        tension: 0.3,
        pointRadius: 4,
        pointBackgroundColor: '#0066ff',
      },
    ],
  };

  return (
    <div style={{
      maxWidth: '700px',
      margin: '30px auto',
      padding: '30px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
      borderRadius: '12px',
      background: '#fff',
      textAlign: 'center',
      fontFamily: 'Segoe UI, sans-serif'
    }}>
      <h2>Deepfake Detection</h2>

      <select value={type} onChange={(e) => setType(e.target.value)} style={{ marginBottom: '15px', padding: '8px', borderRadius: '6px', width: '100%' }}>
        <option value="" disabled hidden>Select file type</option>
        <option value="image">Image</option>
        <option value="video">Video</option>
      </select>

      <input type="file" accept={type === 'image' ? "image/*" : "video/*"} onChange={handleFileChange} style={{ marginBottom: '15px' }} />

      {filePreview && (
        <div>
          <h4>File Preview:</h4>
          {type === 'image' ? (
            <img src={filePreview} alt="Preview" style={{ maxWidth: '100%', maxHeight: '250px', marginBottom: '15px', objectFit: 'contain' }} />
          ) : (
            <video controls style={{ maxWidth: '100%', maxHeight: '250px', marginBottom: '15px' }}>
              <source src={filePreview} />
            </video>
          )}
        </div>
      )}

      <button onClick={handleSubmit} disabled={loading} style={{
        backgroundColor: '#0066ff',
        color: '#fff',
        border: 'none',
        padding: '12px 18px',
        borderRadius: '6px',
        cursor: 'pointer',
        fontWeight: 'bold',
        width: '100%'
      }}>
        {loading ? "Detecting..." : "Submit"}
      </button>

      {result && (
        <div style={{
          marginTop: '20px',
          color: result === 'REAL' ? 'green' : 'red',
          fontSize: '20px',
          fontWeight: 'bold'
        }}>
          <p>Result: {result}</p>
          {confidence !== null && <p>Confidence: {confidence}%</p>}
        </div>
      )}

      {result && analysisDetails.framesAnalyzed && (
        <div>
          <h4>Details:</h4>
          <p>Frames Analyzed: {analysisDetails.framesAnalyzed}</p>
          <p>Processing Time: {analysisDetails.processingTime} seconds</p>
          <p>Model Confidence: {analysisDetails.modelConfidence}%</p>
          <p>Frames Used: {analysisDetails.analyzedFrames}</p>
        </div>
      )}

      {confidence !== null && (
        <div style={{ marginTop: '30px' }}>
          <h4>Confidence Distribution</h4>
          <Pie data={pieData} />
        </div>
      )}

      {performanceData.length > 0 && (
        <div style={{ marginTop: '30px' }}>
          <h4>Per-Frame Confidence</h4>
          <Line data={performanceChartData} />
        </div>
      )}
    </div>
  );
}

export default DeepfakeDetection;

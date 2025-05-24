import React from 'react';
import { useNavigate } from 'react-router-dom';

function Cards({ user }) {
  const navigate = useNavigate();

  const handleCardClick = () => {
    navigate('/detect');
  };

  return (
    <div 
      className="card shadow-lg text-center" 
      style={{ cursor: 'pointer' }} 
      onClick={handleCardClick}
    >
      <img 
        src={user.avatar} 
        className="card-img-top rounded-circle mx-auto mt-3" 
        alt="User" 
        style={{ width: "100px", height: "100px" }} 
      />
      <div className="card-body">
        <h5 className="card-title">{user.first_name} {user.last_name}</h5>
        <p className="card-text text-muted">{user.email}</p>
      </div>
    </div>
  );
}

export default Cards;

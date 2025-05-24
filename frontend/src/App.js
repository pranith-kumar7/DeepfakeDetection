// frontend/src/App.js
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import './App.css';
import RootLayout from './RootLayout';
import Home from './Components/Home';
import Login from './Components/Login';
import Webhome from './Components/Webhome';
import DeepfakeDetection from './Components/DeepfakeDetection';

function App() {
  let browserrouter = createBrowserRouter([
    {
      path: '',
      element: <RootLayout />,
      children: [
        {
          path: '',
          element: <Webhome />,
        },
        {
          path: 'home',
          element: <Home />,
        },
        {
          path: 'login',
          element: <Login />,
        },
        {
          path: 'detect',
          element: <DeepfakeDetection />, // Deepfake detection route
        },
      ],
    },
  ]);

  return (
    <div>
      <RouterProvider router={browserrouter} />
    </div>
  );
}

export default App;

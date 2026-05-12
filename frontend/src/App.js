import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import './App.css';
import RootLayout from './RootLayout';
import Webhome from './Components/Webhome';
import Login from './Components/Login';
import DeepfakeDetection from './Components/DeepfakeDetection';

const browserRouter = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <Webhome />,
      },
      {
        path: 'auth',
        element: <Login />,
      },
      {
        path: 'login',
        element: <Login initialMode="signin" />,
      },
      {
        path: 'signup',
        element: <Login initialMode="signup" />,
      },
      {
        path: 'detect',
        element: <DeepfakeDetection />,
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={browserRouter} />;
}

export default App;

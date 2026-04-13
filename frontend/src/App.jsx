import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';
import Dashboard from './pages/dashboard/Dashboard';
import ConvoAI from './pages/convoai/ConvoAI';

function App() {
  return (
  <div className="container">
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/interview" element={<ConvoAI />} />
      </Routes>
    </BrowserRouter>
  </div>
  );
}

export default App;

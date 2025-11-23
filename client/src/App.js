import { BrowserRouter, Routes, Route } from "react-router-dom";
import Chat from "./pages/Chat";
import './assets/css/style.css';


export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Chat />} />
      </Routes>
    </BrowserRouter>
  );
}

import { Navigate, NavLink, Route, Routes, useNavigate } from "react-router-dom";
import { auth } from "./api";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Orders from "./pages/Orders";
import Positions from "./pages/Positions";
import Broker from "./pages/Broker";

function RequireAuth({ children }) {
  return auth.access ? children : <Navigate to="/login" replace />;
}

function Layout({ children }) {
  const navigate = useNavigate();
  const logout = () => {
    auth.clear();
    navigate("/login");
  };
  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">Quant<span>Power</span> <small>mini</small></div>
        <nav>
          <NavLink to="/" end>Market</NavLink>
          <NavLink to="/orders">Orders</NavLink>
          <NavLink to="/positions">Positions</NavLink>
          <NavLink to="/broker">Broker</NavLink>
        </nav>
        <button className="ghost" onClick={logout}>Logout</button>
      </header>
      <main>{children}</main>
    </div>
  );
}

export default function App() {
  const page = (el) => <RequireAuth><Layout>{el}</Layout></RequireAuth>;
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={page(<Dashboard />)} />
      <Route path="/orders" element={page(<Orders />)} />
      <Route path="/positions" element={page(<Positions />)} />
      <Route path="/broker" element={page(<Broker />)} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function Button({ icon, children, onClick, className }) {
  return (
    <button className={`session-btn ${className ?? ""}`} onClick={onClick}>
      {icon}
      {children}
    </button>
  );
}
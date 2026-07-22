const ErrorMessage = ({ message, onRetry }) => (
  <div className="error-state">
    <p>{message}</p>
    {onRetry && <button onClick={onRetry}>Tentar novamente</button>}
  </div>
);

export default ErrorMessage;

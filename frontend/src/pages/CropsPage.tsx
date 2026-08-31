import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

// Match the backend's CropListResponse schema
interface CropListResponse {
  crops: string[];
}

const fetchSupportedCrops = async (): Promise<CropListResponse> => {
  const response = await fetch(`${import.meta.env.VITE_API_URL || ""}/crops`);
  if (!response.ok) {
    throw new Error("Failed to fetch supported crops");
  }
  return response.json();
};

export function CropsPage() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["supportedCrops"],
    queryFn: fetchSupportedCrops,
  });

  // Extract the array from the response object
  const crops = data?.crops || [];

  return (
    <div className="page-container crops-page">
      <header className="page-header">
        <h1>Supported Crops</h1>
        <p>
          Our AI diagnostic model is currently trained to identify diseases and pests for the following crops. 
          Select a crop to learn more, or head to the scanner to start a diagnosis.
        </p>
        <div className="header-actions">
          <Link to="/scan" className="btn btn-primary">Start a Scan</Link>
          <Link to="/" className="btn btn-secondary">Back to Home</Link>
        </div>
      </header>

      <main className="page-content">
        {isLoading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading supported crops...</p>
          </div>
        )}

        {isError && (
          <div className="error-state">
            <h3>Error loading crops</h3>
            <p>{error instanceof Error ? error.message : "An unknown error occurred."}</p>
            <button onClick={() => window.location.reload()} className="btn btn-outline">
              Try Again
            </button>
          </div>
        )}

        {!isLoading && !isError && crops.length === 0 && (
          <div className="empty-state">
            <p>No crops are currently configured in the system.</p>
          </div>
        )}

        {!isLoading && !isError && crops.length > 0 && (
          <div className="crops-grid">
            {crops.map((crop, index) => (
              <div key={index} className="crop-card">
                <div className="crop-card-image-placeholder">
                  <span className="crop-initial">{crop.charAt(0).toUpperCase()}</span>
                </div>
                <div className="crop-card-content">
                  <h3 className="crop-name">{crop}</h3>
                  <div className="crop-status">
                    <span className="status-badge success">AI Supported</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
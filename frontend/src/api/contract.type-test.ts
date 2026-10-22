import { contractRequest } from "./contract";

contractRequest("/api/v1/alerts", "get", {
  query: { lang: "hi", limit: 20 },
});
contractRequest("/api/v1/alerts/{alert_id}/read", "post", {
  pathParams: { alert_id: 1 },
});
contractRequest("/api/v1/auth/login", "post", {
  data: { identifier: "farmer@example.com", password: "password" },
});
contractRequest("/api/v1/farm/plots/{plot_id}", "put", {
  pathParams: { plot_id: 1 },
  data: { name: "North field", crop: "wheat", reset_geometry: false },
});

// @ts-expect-error The generated path supports GET, not POST.
contractRequest("/api/v1/alerts", "post", {});
contractRequest("/api/v1/alerts/{alert_id}/read", "post", {
  // @ts-expect-error alert_id must be numeric.
  pathParams: { alert_id: "1" },
});
contractRequest("/api/v1/alerts", "get", {
  // @ts-expect-error pageSize is not part of the generated query contract.
  query: { pageSize: 20 },
});
contractRequest("/api/v1/auth/login", "post", {
  // @ts-expect-error LoginRequest requires identifier and password.
  data: { identifier: "farmer@example.com" },
});
contractRequest("/api/v1/farm/plots/{plot_id}", "put", {
  // @ts-expect-error The generated path parameter is named plot_id.
  pathParams: { id: 1 },
  data: { name: "North field", crop: "wheat", reset_geometry: false },
});

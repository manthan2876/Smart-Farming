import { contractRequest } from "./contract";
import type { components } from "./generated/openapi";
import type { Farm, Plot } from "./types";

type ApiFarm = components["schemas"]["FarmResponse"];
type ApiPlot = components["schemas"]["PlotResponse"];

function plotFromApi(plot: ApiPlot): Plot {
  return {
    id: plot.id,
    name: plot.name,
    crop: plot.crop ?? undefined,
    area_acres: plot.area_acres ?? undefined,
    status: plot.status,
    geometry: plot.geometry,
  };
}

function farmFromApi(farm: ApiFarm): Farm {
  return {
    id: farm.id,
    name: farm.name ?? "",
    location: farm.location ?? "",
    area_acres: farm.area_acres ?? 0,
    latitude: farm.latitude ?? undefined,
    longitude: farm.longitude ?? undefined,
    crop_history: farm.crop_history,
    boundary: farm.boundary,
    plots: farm.plots.map(plotFromApi),
  };
}

export async function getFarm(token: string, lang?: string) {
  const farm = await contractRequest(
    "/api/v1/farm",
    "get",
    { query: lang ? { lang } : undefined },
    token,
  );
  return farmFromApi(farm);
}

export async function saveFarm(farm: Omit<Farm, "id">, token: string) {
  const savedFarm = await contractRequest(
    "/api/v1/farm",
    "put",
    {
      data: {
        name: farm.name,
        location: farm.location,
        area_acres: farm.area_acres,
        latitude: farm.latitude,
        longitude: farm.longitude,
        crop_history: farm.crop_history,
        boundary: farm.boundary,
        reset_boundary: false,
      },
    },
    token,
  );
  return farmFromApi(savedFarm);
}

export async function createPlot(
  plot: {
    name: string;
    crop: string | null;
    area_acres: number | null;
    geometry?: Record<string, unknown> | null;
  },
  token: string,
) {
  const createdPlot = await contractRequest("/api/v1/farm/plots", "post", {
    data: { ...plot, reset_geometry: false },
  }, token);
  return plotFromApi(createdPlot);
}

export async function updatePlot(
  id: number,
  plot: {
    name: string;
    crop: string | null;
    area_acres: number | null;
    geometry?: Record<string, unknown> | null;
  },
  token: string,
) {
  const updatedPlot = await contractRequest(
    "/api/v1/farm/plots/{plot_id}",
    "put",
    {
      pathParams: { plot_id: id },
      data: { ...plot, reset_geometry: false },
    },
    token,
  );
  return plotFromApi(updatedPlot);
}

export async function deletePlot(id: number, token: string) {
  return contractRequest(
    "/api/v1/farm/plots/{plot_id}",
    "delete",
    { pathParams: { plot_id: id } },
    token,
  );
}

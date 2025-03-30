import { Button } from "@/components/ui/button";
import {
  fetchMapData,
  importConnections,
  importDirections,
  deleteAllMapData,
} from "@/services/APIs/mapAPI";
import { AxiosResponse } from "axios";
import { FileUp } from "lucide-react";
import Papa from "papaparse";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AccordionCSVMapGuide } from "./AccordionCSVMapGuide";
import { AlertMapGuide } from "./AlertMapGuide";
import { DownloadSampleCSVFilesForMap } from "./DownloadSampleCSVFilesForMap";
import { MapVisualizer } from "./MapVisualizer";

interface MapData {
  nodes: number[];
  connections: { node1: number; node2: number; distance: number }[];
  directions: { node1: number; node2: number; direction: number }[];
}

export function PageMap() {
  const [mapData, setMapData] = useState<MapData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const resetFileInputs = () => {
    const connFileInput = document.getElementById(
      "conn-file",
    ) as HTMLInputElement;
    const dirFileInput = document.getElementById(
      "dir-file",
    ) as HTMLInputElement;

    if (connFileInput) connFileInput.value = ""; // Reset the value of the connection file input
    if (dirFileInput) dirFileInput.value = ""; // Reset the value of the direction file input
  };

  const handleDeleteAllMapData = async () => {
    try {
      await deleteAllMapData(); // Call the API to delete all map data
      toast.success("All map data deleted successfully.");
      setMapData(null); // Clear the map data from the UI
      setError(null); // Clear any errors
      resetFileInputs(); // Reset the file inputs
    } catch (error) {
      toast.error("Failed to delete map data.");
      console.error("Error deleting map data:", error);
    }
  };

  const handleFileImport = (
    event: React.ChangeEvent<HTMLInputElement>,
    importFunction: (csvData: string) => Promise<AxiosResponse<unknown>>,
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    Papa.parse(file, {
      complete: async (result: { data: string[][] }) => {
        const csvData = result.data
          .map((row: string[]) => row.join(","))
          .join("\n");
        await importFunction(csvData);
        toast.success("Import successful");
      },
      skipEmptyLines: true,
    });
  };

  const handleShowMap = async () => {
    const data = (await fetchMapData()) as MapData;
    console.log("Fetched map data:", data); // Debug log

    if (!data || !data.nodes || !data.connections || !data.directions) {
      toast.error("Failed to load map data.");
      setError("Incomplete data: Please ensure both CSV files are imported.");
      setMapData(null);
      return;
    }
    // Validate that connections and directions are related
    const allNodes = new Set(data.nodes);
    const invalidConnections = data.connections.some(
      (conn: { node1: number; node2: number; distance: number }) =>
        !allNodes.has(conn.node1) || !allNodes.has(conn.node2),
    );
    const invalidDirections = data.directions.some(
      (dir: { node1: number; node2: number; direction: number }) =>
        !allNodes.has(dir.node1) || !allNodes.has(dir.node2),
    );

    if (invalidConnections || invalidDirections) {
      setError(
        "Invalid data: Connections or directions do not match the nodes.",
      );
      setMapData(null);
      return;
    }

    setError(null); // Clear any previous errors
    setMapData(data);
  };

  useEffect(() => {
    handleShowMap();
  }, []);

  return (
    <div className="space-y-5">
      <h2 className="text-3xl font-bold">Map</h2>
      <AlertMapGuide />
      <AccordionCSVMapGuide />
      <div className="space-x-5">
        <Button onClick={() => document.getElementById("conn-file")?.click()}>
          <FileUp />
          Import 1st CSV
        </Button>
        <input
          id="conn-file"
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => handleFileImport(e, importConnections)}
        />

        <Button onClick={() => document.getElementById("dir-file")?.click()}>
          <FileUp />
          Import 2nd CSV
        </Button>
        <input
          id="dir-file"
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => handleFileImport(e, importDirections)}
        />

        <Button variant={"secondary"} onClick={handleShowMap}>
          Show map image
        </Button>

        <Button variant={"destructive"} onClick={handleDeleteAllMapData}>
          Delete All Map Data
        </Button>

        <DownloadSampleCSVFilesForMap />
      </div>
      {error ? (
        <div className="font-bold text-red-500">{error}</div>
      ) : (
        mapData && <MapVisualizer data={mapData} />
      )}
    </div>
  );
}

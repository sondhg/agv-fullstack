import { Button } from "@/components/ui/button";
import {
  fetchMapData,
  importConnections,
  importDirections,
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

  const handleFileImport = (
    event: React.ChangeEvent<HTMLInputElement>,
    importFunction: (csvData: string) => Promise<AxiosResponse<any, any>>,
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    Papa.parse(file, {
      complete: async (result: { data: string[][] }) => {
        const csvData = result.data.map((row: any) => row.join(",")).join("\n");
        await importFunction(csvData);
        toast.success("Import successful");
      },
      skipEmptyLines: true,
    });
  };

  const handleShowMap = async () => {
    const data = await fetchMapData();
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

  // Automatically fetch and display the map data when the component mounts
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

        <Button
          variant={"secondary"}
          onClick={() => document.getElementById("dir-file")?.click()}
        >
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

        <Button variant={"destructive"} onClick={handleShowMap}>
          Show map image
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

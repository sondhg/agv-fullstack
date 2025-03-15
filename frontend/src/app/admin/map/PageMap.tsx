import { Button } from "@/components/ui/button";
import {
  fetchMapData,
  importConnections,
  importDirections,
} from "@/services/APIs/mapAPI";
import Papa from "papaparse";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export function PageMap() {
  const [mapData, setMapData] = useState<{
    nodes: number[];
    connections: { node1: number; node2: number; distance: number }[];
    directions: { node1: number; node2: number; direction: number }[];
  } | null>(null);

  const [error, setError] = useState<string | null>(null);

  const handleFileImport = (
    event: React.ChangeEvent<HTMLInputElement>,
    importFunction: Function,
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    Papa.parse(file, {
      complete: async (result) => {
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
      <div className="space-x-5">
        <Button onClick={() => document.getElementById("conn-file")?.click()}>
          Import CSV for connection and distance
        </Button>
        <input
          id="conn-file"
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => handleFileImport(e, importConnections)}
        />

        <Button onClick={() => document.getElementById("dir-file")?.click()}>
          Import CSV for relative directions
        </Button>
        <input
          id="dir-file"
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => handleFileImport(e, importDirections)}
        />

        <Button onClick={handleShowMap}>Show map image</Button>
      </div>
      {error ? (
        <div className="font-bold text-red-500">{error}</div>
      ) : (
        mapData && <MapVisualizer data={mapData} />
      )}
    </div>
  );
}

export const MapVisualizer = ({ data }: { data: any }) => {
  const [positions, setPositions] = useState<{
    [key: number]: { x: number; y: number };
  }>({});
  const [scaledPositions, setScaledPositions] = useState<{
    [key: number]: { x: number; y: number };
  }>({});

  useEffect(() => {
    if (!data || !data.nodes || !data.connections) {
      console.error("Invalid data structure:", data);
      return;
    }

    const newPositions: { [key: number]: { x: number; y: number } } = {};
    const visitedNodes = new Set<number>();
    const queue: { node: number; x: number; y: number }[] = [];

    // Start at the center of the grid
    const startX = 500; // Arbitrary starting x-coordinate
    const startY = 500; // Arbitrary starting y-coordinate
    queue.push({ node: data.nodes[0], x: startX, y: startY });
    newPositions[data.nodes[0]] = { x: startX, y: startY };

    while (queue.length > 0) {
      const { node, x, y } = queue.shift()!;
      visitedNodes.add(node);

      // Find all connections for the current node
      data.connections
        .filter((conn: any) => conn.node1 === node || conn.node2 === node)
        .forEach((conn: any) => {
          const neighbor = conn.node1 === node ? conn.node2 : conn.node1;
          if (!visitedNodes.has(neighbor)) {
            const distance = conn.distance * 10; // Scale distance for visualization
            let newX = x;
            let newY = y;

            // Determine position based on direction
            const direction = data.directions.find(
              (dir: any) => dir.node1 === node && dir.node2 === neighbor,
            )?.direction;

            if (!direction) {
              console.error(
                `Direction not found for nodes ${node} -> ${neighbor}`,
              );
              return;
            }

            switch (direction) {
              case 1: // North
                newY = y - distance;
                break;
              case 2: // East
                newX = x + distance;
                break;
              case 3: // South
                newY = y + distance;
                break;
              case 4: // West
                newX = x - distance;
                break;
              default:
                console.error(
                  `Invalid direction ${direction} for nodes ${node} -> ${neighbor}`,
                );
                return;
            }

            newPositions[neighbor] = { x: newX, y: newY };
            queue.push({ node: neighbor, x: newX, y: newY });
          }
        });
    }

    setPositions(newPositions);

    // Scale positions to fit within the canvas
    const allX = Object.values(newPositions).map((pos) => pos.x);
    const allY = Object.values(newPositions).map((pos) => pos.y);
    const minX = Math.min(...allX);
    const maxX = Math.max(...allX);
    const minY = Math.min(...allY);
    const maxY = Math.max(...allY);

    const canvasWidth = 1000; // Canvas width
    const canvasHeight = 1000; // Canvas height
    const padding = 50; // Padding around the edges

    const scaleX = (canvasWidth - 2 * padding) / (maxX - minX || 1);
    const scaleY = (canvasHeight - 2 * padding) / (maxY - minY || 1);
    const scale = Math.min(scaleX, scaleY); // Maintain aspect ratio

    const scaled = Object.fromEntries(
      Object.entries(newPositions).map(([node, pos]) => [
        node,
        {
          x: padding + (pos.x - minX) * scale,
          y: padding + (pos.y - minY) * scale,
        },
      ]),
    );

    setScaledPositions(scaled);
  }, [data]);

  return (
    <div className="relative border border-gray-300 p-5">
      <svg
        viewBox="0 0 1000 1000"
        preserveAspectRatio="xMidYMid meet"
        width="100%"
        height="auto"
        className="border border-gray-400 bg-white"
      >
        {data.connections.map((conn: any, index: number) => {
          const pos1 = scaledPositions[conn.node1];
          const pos2 = scaledPositions[conn.node2];

          if (!pos1 || !pos2) return null;

          // Calculate the midpoint of the line
          const midX = (pos1.x + pos2.x) / 2;
          const midY = (pos1.y + pos2.y) / 2;

          // Determine the orientation of the line
          const isHorizontal =
            Math.abs(pos1.y - pos2.y) < Math.abs(pos1.x - pos2.x);
          const isVertical =
            Math.abs(pos1.x - pos2.x) < Math.abs(pos1.y - pos2.y);

          // Adjust the offset based on the orientation
          const offsetX = isVertical ? 10 : 0; // Offset horizontally for vertical lines
          const offsetY = isHorizontal ? -10 : isVertical ? 0 : -10; // Offset vertically for horizontal/diagonal lines

          return (
            <g key={index}>
              <line
                x1={pos1.x}
                y1={pos1.y}
                x2={pos2.x}
                y2={pos2.y}
                stroke="black"
                strokeWidth="2"
              />
              <text
                x={midX + offsetX}
                y={midY + offsetY}
                textAnchor="middle"
                fontSize="12"
                fill="red"
              >
                {conn.distance}
              </text>
            </g>
          );
        })}

        {data.nodes.map((node: number) => {
          const pos = scaledPositions[node];
          return (
            pos && (
              <circle
                key={node}
                cx={pos.x}
                cy={pos.y}
                r="15"
                fill="lightblue"
                stroke="black"
              />
            )
          );
        })}

        {data.nodes.map((node: number) => {
          const pos = scaledPositions[node];
          return (
            pos && (
              <text
                key={`text-${node}`}
                x={pos.x}
                y={pos.y}
                textAnchor="middle"
                dy=".3em"
                fontSize="12"
              >
                {node}
              </text>
            )
          );
        })}
      </svg>
    </div>
  );
};

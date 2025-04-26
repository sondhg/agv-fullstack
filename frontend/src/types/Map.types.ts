interface MapData {
  nodes: number[];
  connections: { node1: number; node2: number; distance: number }[];
  directions: { node1: number; node2: number; direction: number }[];
}

interface Connection {
  node1: number;
  node2: number;
  distance: number;
}

interface Direction {
  node1: number;
  node2: number;
  direction: number;
}

export type { Connection, Direction, MapData };

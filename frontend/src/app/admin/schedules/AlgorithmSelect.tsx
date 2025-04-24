import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface AlgorithmSelectProps {
  selectedAlgorithm: string;
  onAlgorithmChange: (value: string) => void;
}

export function AlgorithmSelect({
  selectedAlgorithm,
  onAlgorithmChange,
}: AlgorithmSelectProps) {
  return (
    <Select
      onValueChange={onAlgorithmChange} // Pass the selected algorithm to the parent
      defaultValue={selectedAlgorithm} // Default value
    >
      <SelectTrigger>
        <SelectValue placeholder="Select Algorithm" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>Algorithms</SelectLabel>
          <SelectItem value="dijkstra">Dijkstra</SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>
  );
}

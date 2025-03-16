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

export const AlgorithmSelect: React.FC<AlgorithmSelectProps> = ({
  selectedAlgorithm,
  onAlgorithmChange,
}) => {
  return (
    <Select
      onValueChange={onAlgorithmChange} // Pass the selected algorithm to the parent
      defaultValue={selectedAlgorithm} // Default value
    >
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Select Algorithm" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>Algorithms</SelectLabel>
          <SelectItem value="dijkstra">Dijkstra</SelectItem>
          <SelectItem value="q_learning">Q-Learning</SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>
  );
};

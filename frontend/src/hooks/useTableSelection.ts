import { OnChangeFn, RowSelectionState } from "@tanstack/react-table";
import { useEffect, useState } from "react";

export interface UseTableSelectionResult {
  rowSelection: RowSelectionState;
  setRowSelection: OnChangeFn<RowSelectionState>;
  selectedIds: number[];
  setSelectedIds: (value: number[]) => void;
  resetSelection: () => void;
}

export function useTableSelection<T>(
  listData: T[],
  idKey: keyof T,
): UseTableSelectionResult {
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  // Reset selection state
  const resetSelection = () => {
    setRowSelection({});
    setSelectedIds([]);
  };

  const handleRowSelectionChange: OnChangeFn<RowSelectionState> = (
    updaterOrValue,
  ) => {
    const newValue =
      typeof updaterOrValue === "function"
        ? updaterOrValue(rowSelection)
        : updaterOrValue;
    setRowSelection(newValue);
  };

  useEffect(() => {
    // Convert row selection to IDs safely
    const ids = Object.entries(rowSelection)
      .filter(([, selected]) => selected)
      .map(([index]) => {
        const item = listData[parseInt(index)];
        return item ? Number(item[idKey]) : null;
      })
      .filter((id): id is number => id !== null);

    setSelectedIds(ids);

    // Clean up any invalid selections
    const validSelections = Object.entries(rowSelection).reduce(
      (acc, [index, selected]) => {
        if (selected && listData[parseInt(index)]) {
          acc[index] = true;
        }
        return acc;
      },
      {} as RowSelectionState,
    );

    if (
      Object.keys(validSelections).length !== Object.keys(rowSelection).length
    ) {
      setRowSelection(validSelections);
    }
  }, [rowSelection, listData, idKey]);

  return {
    rowSelection,
    setRowSelection: handleRowSelectionChange,
    selectedIds,
    setSelectedIds,
    resetSelection,
  };
}

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createAGVsViaCSV } from "@/services/APIs/agvsAPI";
import { Upload } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

interface DialogCSVUploadProps {
  isDialogOpen: boolean;
  setIsDialogOpen: (open: boolean) => void;
  onSuccess: () => void;
}

export function DialogCSVUpload({
  isDialogOpen,
  setIsDialogOpen,
  onSuccess,
}: DialogCSVUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.name.toLowerCase().endsWith(".csv")) {
        toast.error("Please select a CSV file");
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error("Please select a CSV file");
      return;
    }

    try {
      setIsUploading(true);
      const response = await createAGVsViaCSV(selectedFile);

      if (response.success) {
        const count = response.created_agvs?.length || 0;
        toast.success(`Successfully created ${count} AGVs from CSV file`);
        setIsDialogOpen(false);
        setSelectedFile(null);
        onSuccess();
      } else {
        toast.error(response.message || "Failed to create AGVs");
      }
    } catch (error) {
      let errorMessage = "Failed to upload CSV file";

      if (error instanceof Error) {
        errorMessage = error.message;
      }

      toast.error(errorMessage);
      console.error("Error uploading CSV:", error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDialogClose = () => {
    if (!isUploading) {
      setIsDialogOpen(false);
      setSelectedFile(null);
    }
  };

  return (
    <Dialog open={isDialogOpen} onOpenChange={handleDialogClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create AGVs via CSV</DialogTitle>
          <DialogDescription>
            Upload a CSV file to create multiple AGVs at once. The CSV file
            should have two columns: agv_id and preferred_parking_node.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="csv-file">CSV File</Label>
            <Input
              id="csv-file"
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              disabled={isUploading}
            />
            {selectedFile && (
              <p className="text-sm text-muted-foreground">
                Selected: {selectedFile.name}
              </p>
            )}
          </div>

          <div className="rounded-md border p-3 text-sm">
            <p className="mb-2 font-medium">Expected CSV format:</p>
            <pre className="text-xs text-muted-foreground">
              {`agv_id,preferred_parking_node,
1,8,
2,9,
3,16,`}
            </pre>
          </div>
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={handleDialogClose}
            disabled={isUploading}
          >
            Cancel
          </Button>
          <Button
            type="button"
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
          >
            <Upload className="mr-2 h-4 w-4" />
            {isUploading ? "Uploading..." : "Upload & Create AGVs"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

import { useToast } from "@/hooks/use-toast";
import { useForm } from "react-hook-form";
import { z } from "zod";

interface UseFormDialogOptions<T> {
  defaultValues: T;
  schema: z.ZodSchema;
  onSubmit: (values: T) => Promise<void>;
  successMessage: string;
  errorMessage: string;
  onSuccess?: () => void;
}

export function useFormDialog<T extends Record<string, unknown>>({
  defaultValues,
  schema,
  onSubmit,
  successMessage,
  errorMessage,
  onSuccess,
}: UseFormDialogOptions<T>) {
  const { toast } = useToast();
  const form = useForm<T>({
    resolver: async (data) => {
      try {
        const validatedData = await schema.parseAsync(data);
        return {
          values: validatedData,
          errors: {},
        };
      } catch (error) {
        if (error instanceof z.ZodError) {
          const errors = error.errors.reduce((acc, curr) => {
            const path = curr.path.join(".");
            return { ...acc, [path]: { message: curr.message, type: "validation" } };
          }, {});
          return {
            values: {},
            errors,
          };
        }
        return {
          values: {},
          errors: { "": { type: "validation", message: "Invalid form data" } },
        };
      }
    },
    defaultValues,
    mode: "onChange",
  });

  const handleSubmit = async (values: T) => {
    try {
      await onSubmit(values);
      toast({
        title: successMessage,
        description: JSON.stringify(values, null, 2),
      });
      onSuccess?.();
    } catch (error) {
      console.error("Form submission error:", error);
      toast({
        title: errorMessage,
        description: error instanceof Error ? error.message : "Unknown error occurred",
      });
    }
  };

  return {
    form,
    handleSubmit: form.handleSubmit(handleSubmit),
  };
}
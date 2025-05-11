// filepath: e:\HUST_All\HUST-PROJECT\agv-fullstack\frontend\src\app\admin\agvs\FormSimulateUpdateAgvPositionMQTT.tsx
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  CONNECT_TIMEOUT,
  RECONNECT_PERIOD,
  TOPIC_AGVDATA,
} from "@/constants/mqttConstants";
import { zodResolver } from "@hookform/resolvers/zod";
import mqtt from "mqtt";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

/**
 * Form schema for AGV position update simulation via MQTT
 * Validates that both fields are positive integers
 */
const formSchema = z.object({
  agv_id: z.string().min(1, "AGV ID is required").regex(/^\d+$/, {
    message: "AGV ID must be a positive integer",
  }),
  current_node: z.string().min(1, "Current node is required").regex(/^\d+$/, {
    message: "Current node must be a positive integer",
  }),
});

type FormValues = z.infer<typeof formSchema>;

/**
 * Form component for simulating AGV position updates via MQTT
 *
 * @param props.onUpdateSuccess - Callback function to run after successful position update
 */
export const FormSimulateUpdateAgvPositionMQTT = ({
  onUpdateSuccess,
}: {
  onUpdateSuccess?: () => Promise<void>;
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [client, setClient] = useState<mqtt.MqttClient | null>(null);
  const [connectionStatus, setConnectionStatus] =
    useState<string>("Disconnected");
  const [lastResponse, setLastResponse] = useState<string | null>(null);
  const [connectionAttempts, setConnectionAttempts] = useState(0);

  // Initialize form with React Hook Form and Zod validation
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      agv_id: "",
      current_node: "",
    },
    mode: "onChange",
  }); // Function to create MQTT connection
  const connectToMqtt = () => {
    setConnectionStatus("Connecting...");
    setConnectionAttempts((prev) => prev + 1);

    // Use WebSockets for browser clients
    // broker.emqx.io provides a WebSocket endpoint on port 8083 (unencrypted) or 8084 (encrypted)
    const mqttClient = mqtt.connect("ws://broker.emqx.io:8083/mqtt", {
      clientId: `agv_frontend_${Math.random().toString(16).substring(2, 10)}`, // Generate random client ID
      clean: true, // Non-persistent session
      reconnectPeriod: RECONNECT_PERIOD, // Try to reconnect every 5 seconds
      connectTimeout: CONNECT_TIMEOUT, // 30 seconds timeout
    });

    return mqttClient;
  };

  // Connect to MQTT broker on component mount
  useEffect(() => {
    const mqttClient = connectToMqtt();
    mqttClient.on("connect", () => {
      console.log(
        "Connected to MQTT broker at broker.emqx.io:8083 via WebSockets",
      );
      setConnectionStatus("Connected");
      toast.success("Connected to MQTT broker via WebSockets");
      // Subscribe to response topics when connection is established
      // We're subscribing to all AGV route topics using wildcard
      mqttClient.subscribe("agvroute/+", (err) => {
        if (err) {
          console.error("Error subscribing to response topics:", err);
        } else {
          console.log("Subscribed to AGV response topics (agvroute/+)");
        }
      });
    });

    // Handle incoming messages (responses from server)
    mqttClient.on("message", (topic, message) => {
      try {
        const responseData = JSON.parse(message.toString());
        console.log(`Received response on topic ${topic}:`, responseData);
        setLastResponse(JSON.stringify(responseData, null, 2));

        // Show toast notification for the response
        const agvId = topic.split("/")[1]; // Extract AGV ID from topic
        toast.info(`Received response for AGV ${agvId}`, {
          description: `Motion state: ${responseData.motion_state || "unknown"}`,
        });
      } catch (error) {
        console.error("Error processing message:", error);
      }
    });
    mqttClient.on("error", (err) => {
      console.error("MQTT connection error:", err);
      setConnectionStatus(`Error: ${err.message}`);
      toast.error(`MQTT connection error: ${err.message}`);
    });

    mqttClient.on("disconnect", () => {
      console.log("MQTT disconnected");
      setConnectionStatus("Disconnected");
      toast.warning("Disconnected from MQTT broker");
    });

    mqttClient.on("reconnect", () => {
      console.log("Attempting to reconnect to MQTT broker");
      setConnectionStatus("Reconnecting...");
    });

    mqttClient.on("close", () => {
      console.log("MQTT connection closed");
      setConnectionStatus("Disconnected");
    });

    // Store the client in state
    setClient(mqttClient);

    // Clean up on component unmount
    return () => {
      if (mqttClient) {
        mqttClient.end();
      }
    };
  }, []);

  /**
   * Handle form submission
   * Publishes the AGV ID and current node to the MQTT topic
   *
   * @param values - Form values containing agv_id and current_node
   */
  const onSubmit = async (values: FormValues) => {
    if (!client) {
      toast.error("MQTT client not connected");
      return;
    }

    setIsSubmitting(true);
    try {
      // Convert string values to numbers
      const agvId = parseInt(values.agv_id, 10);
      const currentNode = parseInt(values.current_node, 10);

      // Create the MQTT message payload
      const payload = JSON.stringify({
        agv_id: agvId,
        current_node: currentNode,
      });

      // Publish to the topic agvdata/{agv_id}
      const topic = `${TOPIC_AGVDATA}/${agvId}`;
      client.publish(topic, payload, { qos: 1 }, (error) => {
        if (error) {
          console.error("Failed to publish message:", error);
          toast.error(`Failed to publish message: ${error.message}`);
        } else {
          console.log(`Message published to ${topic}: ${payload}`);
          toast.success(`AGV position update sent via MQTT to topic ${topic}`);

          // Call the onUpdateSuccess callback if provided
          if (onUpdateSuccess) {
            onUpdateSuccess();
          }
        }
        setIsSubmitting(false);
      });
    } catch (error) {
      console.error("Error sending MQTT message:", error);
      toast.error(
        `Error sending MQTT message: ${error instanceof Error ? error.message : String(error)}`,
      );
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      {" "}
      <CardHeader>
        <CardTitle>Simulate AGV Position Update via MQTT</CardTitle>
        <p className="mt-1 text-xs text-muted-foreground">
          Connecting to broker.emqx.io:8083 via WebSockets (ws://)
        </p>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          {" "}
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="mr-2 text-sm font-medium">MQTT Status:</span>
              <span
                className={`text-sm ${
                  connectionStatus === "Connected"
                    ? "text-green-500"
                    : connectionStatus === "Connecting..." ||
                        connectionStatus === "Reconnecting..."
                      ? "text-yellow-500"
                      : "text-red-500"
                }`}
              >
                {connectionStatus}
              </span>
              <span className="ml-2 text-xs text-muted-foreground">
                (Attempts: {connectionAttempts})
              </span>
            </div>
            <div className="flex items-center gap-4">
              {connectionStatus !== "Connected" && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setClient(connectToMqtt());
                  }}
                >
                  Reconnect
                </Button>
              )}
              {lastResponse && (
                <div className="text-xs text-muted-foreground">
                  Last response received
                </div>
              )}
            </div>
          </div>
          {lastResponse && (
            <div className="mt-2 rounded-md bg-muted p-2">
              <pre className="max-h-24 overflow-auto text-xs">
                {lastResponse}
              </pre>
            </div>
          )}
        </div>
        <div>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <div className="flex flex-col gap-4 md:flex-row">
                <FormField
                  control={form.control}
                  name="agv_id"
                  render={({ field }) => (
                    <FormItem className="flex-1">
                      <FormLabel>AGV ID</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Enter ID of AGV"
                          type="text"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="current_node"
                  render={({ field }) => (
                    <FormItem className="flex-1">
                      <FormLabel>Current Node</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Enter current position"
                          type="text"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button
                  type="submit"
                  className="w-full md:w-auto md:self-end"
                  disabled={
                    isSubmitting ||
                    !form.formState.isValid ||
                    connectionStatus !== "Connected"
                  }
                >
                  {isSubmitting ? "Sending..." : "Send via MQTT"}
                </Button>
              </div>
            </form>
          </Form>
        </div>
      </CardContent>
    </Card>
  );
};

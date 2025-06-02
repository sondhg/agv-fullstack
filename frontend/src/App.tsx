import { ThemeProvider } from "@/components/theme-provider";
import { Toaster as ToasterSonner } from "@/components/ui/sonner";
import { Toaster as ToasterToast } from "@/components/ui/toaster";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ErrorBoundary } from "react-error-boundary";
import { Provider } from "react-redux";
import { PersistGate } from "redux-persist/integration/react";
import { persistor, store } from "./redux/store";
import { AllRoutes } from "./routes/AllRoutes";

// Create a client
const queryClient = new QueryClient();

function App() {
  const Fallback = ({ error }: { error: Error }) => (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre className="text-red-500">{error.message}</pre>
      <pre>{error.stack}</pre>
    </div>
  );

  return (
    <>
      <ErrorBoundary FallbackComponent={Fallback}>
        <Provider store={store}>
          <PersistGate loading={null} persistor={persistor}>
            <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
              <QueryClientProvider client={queryClient}>
                <AllRoutes />
              </QueryClientProvider>
            </ThemeProvider>
          </PersistGate>
        </Provider>
        {/* Toasters at top level */}
        <ToasterSonner
          richColors
          theme="light"
          toastOptions={{}}
          position="top-right"
          duration={1500}
        />
        <ToasterToast />
      </ErrorBoundary>
    </>
  );
}

export default App;

import React from 'react';

type Props = React.PropsWithChildren<{}>;
type State = { hasError: boolean; error?: Error };

export default class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  private handleReload = () => {
    window.location.assign('/');
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-lg w-full space-y-4 rounded-md border border-red-200 bg-white p-6 shadow-sm">
            <h1 className="text-xl font-semibold text-red-700">Something went wrong</h1>
            <p className="text-sm text-gray-700">
              An unexpected error occurred. Try reloading or going back to the dashboard. If the issue
              persists, contact support.
            </p>
            {import.meta.env.DEV && this.state.error && (
              <pre className="overflow-auto rounded bg-red-50 p-3 text-xs text-red-800">
                {String(this.state.error?.message || this.state.error)}
              </pre>
            )}
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() =>
                  window.history.length > 1 ? window.history.back() : this.handleReload()
                }
                className="rounded-md bg-gray-200 px-4 py-2 text-sm font-medium text-gray-900 hover:bg-gray-300"
              >
                Go Back
              </button>
              <button
                type="button"
                onClick={this.handleReload}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

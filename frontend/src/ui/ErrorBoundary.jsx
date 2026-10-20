import { Component } from "react";
import ErrorState from "./ErrorState";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error("CareerForge UI error:", error, info);
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <div className="cf-page">
        <ErrorState
          message="An unexpected error occurred while displaying this page. Reloading usually fixes it."
          onRetry={() => window.location.reload()}
        />
      </div>
    );
  }
}
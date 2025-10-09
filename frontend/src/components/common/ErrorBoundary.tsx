import React from 'react'

export default class ErrorBoundary extends React.Component<any, any> {
  constructor(props:any){super(props);this.state={hasError:false}}
  static getDerivedStateFromError(){return {hasError:true}}
  render(){return this.state.hasError ? <div>Something went wrong</div> : this.props.children}
}

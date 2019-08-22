import React from 'react'
import ReactDOM, { render } from 'react-dom'

class HTMLComment extends React.Component {
  static defaultProps = {
    trim: true
  }

  componentDidMount() {
    let el = ReactDOM.findDOMNode(this)
    ReactDOM.unmountComponentAtNode(el)
    el.outerHTML = this.createComment()
  }

  createComment() {
    let text = this.props.text

    if (this.props.trim) {
      text = text.trim()
    }

    return `<!-- ${text} -->`
  }

  render() {
    return <div />
  }
}

export default HTMLComment
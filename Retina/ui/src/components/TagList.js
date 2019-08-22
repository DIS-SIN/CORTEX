import React from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faAngleRight } from '@fortawesome/free-solid-svg-icons';

function numberWithCommas(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

class TagList extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div class="row">
        {this.props.tagsData.map(n => {
          return (
            <div class="col-xl-3 col-sm-6 mb-5">
              <div class={"card text-white bg-" + n.color + " o-hidden h-100"}>
                  <div class="card-body">
                  <div class="card-body-icon">
                      <FontAwesomeIcon icon={n.icon} />
                  </div>
                  <div class="mr-5 float-right font-weight-bold">{numberWithCommas(n.size)}</div>
                  <div class="mr-5 clear">{n.label}</div>
                  </div>
                  <a class="card-footer text-white clearfix small z-1" href="#">
                  <span class="float-left">View Details</span>
                  <span class="float-right">
                      <FontAwesomeIcon icon={faAngleRight} />
                  </span>
                  </a>
              </div>
          </div>
          );
        })}
      </div>            
    );
  }
}

export default TagList;

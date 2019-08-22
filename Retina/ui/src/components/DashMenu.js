import React from 'react';
import HTMLComment from './HTMLComment';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFolder, faGraduationCap, faTable, faTachometerAlt, faAngleRight} from '@fortawesome/free-solid-svg-icons';
import { BrowserRouter as Router, Route, Link } from "react-router-dom";

export default class DashMenu extends React.Component{
  
    render(){
        return ( 
            <Router>
                <ul class="sidebar navbar-nav">
                    <li class="nav-item active">
                        <a class="nav-link" href="#">
                            <FontAwesomeIcon icon={faTachometerAlt} />
                        <span>Dashboard</span>
                        </a>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link" href="#" id="pagesDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                            <FontAwesomeIcon icon={faFolder} />
                            <span class="ml-2">Overview <FontAwesomeIcon className="mt-1 float-right text-white" icon={faAngleRight} /></span>
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">
                            <FontAwesomeIcon icon={faGraduationCap} />
                            <span class="ml-2">Courses</span>
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">
                            <FontAwesomeIcon icon={faTable} />
                            <span class="ml-2">Offerings</span>
                        </a>
                    </li>
                </ul>
            </Router>          
        );
    }
  }
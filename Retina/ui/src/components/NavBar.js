import React from 'react';
import HTMLComment from './HTMLComment'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faBars } from '@fortawesome/free-solid-svg-icons'
import TopSearchBar from './TopSearchBar'
import { faUserCircle} from '@fortawesome/free-solid-svg-icons'

export default class NavBar extends React.Component{
  
  render(){
    return (
      <div>
          <HTMLComment text="NavBar" />
          <nav class="navbar navbar-expand navbar-dark bg-dark static-top">
            <a class="navbar-brand mr-1" href="index.html">Retina</a>

            <button class="btn btn-link btn-sm text-white order-1 order-sm-0" id="sidebarToggle" href="#">
              <FontAwesomeIcon icon={faBars} />
            </button>

            <HTMLComment text="Search bar" />
            <TopSearchBar />

            <HTMLComment text="Right Navbar" />
            <ul class="navbar-nav d-flex flex-row-reverse bd-highlight">
              <li class="nav-item dropdown no-arrow">
                <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                  <FontAwesomeIcon icon={faUserCircle} />
                </a>
                <div class="dropdown-menu dropdown-menu-right" aria-labelledby="userDropdown">
                  <a class="dropdown-item" href="#">Settings</a>
                  <a class="dropdown-item" href="#">Activity Log</a>
                  <div class="dropdown-divider"></div>
                  <a class="dropdown-item" href="#" data-toggle="modal" data-target="#logoutModal">Logout</a>
                </div>
              </li>
            </ul>
          </nav>
          <HTMLComment text="End of Right Navbar" />
      </div>
    );
  }
}


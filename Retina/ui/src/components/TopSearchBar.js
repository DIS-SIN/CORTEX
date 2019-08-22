import React from 'react';
import HTMLComment from './HTMLComment'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSearch } from '@fortawesome/free-solid-svg-icons'

export default class TopSearchBar extends React.Component{
  
    render(){
        return (
            <div>
                <HTMLComment text="Topbar Search" />
                <form class="d-flex flex-row-reverse bd-highlight">
                    <div class="input-group">
                    <input type="text" class="form-control" placeholder="Search for..." aria-label="Search" aria-describedby="basic-addon2" />
                    <div class="input-group-append">
                        <button class="btn btn-primary" type="button">
                            <FontAwesomeIcon icon={faSearch} />
                        </button>
                    </div>
                    </div>
                </form>
            </div>
        );
    }
}
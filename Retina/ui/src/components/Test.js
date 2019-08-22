import React from 'react';
import DashTopBar from './DashTopBar'
import HTMLComment from './HTMLComment'
import DashMenu from './DashMenu';
import Learner from './Learner';
import CourseTypes from './CourseTypes';
import ClassDept from './ClassDept';
import InstructorView from './Overview/InstructorView';
import { TextField, Button } from '@material-ui/core';
import Language from './Language';

export default class Test extends React.Component{

    constructor(props) {
        super(props);
    
        this.state = {
          to: "2019-01-01",
          from: "2014-05-01",
          code: "Z132",
          new_code: "Z132"
        };
    }

    getFrom = () => {
        return this.state.from.length > 0
            ? { year_contains: this.state.from }
            : {};
    };

    handleFromChange = from => event => {
        const val = event.target.value;
        this.setState({
          [from]: val
        });
    };

    getTo = () => {
        return this.state.to.length > 0
            ? { year_contains: this.state.to }
            : {};
    };

    handleFromChange = to => event => {
        const val = event.target.value;
        this.setState({
          [to]: val
        });
    };

    getCode = () => {
        return this.state.code.length > 0
            ? { code_contains: this.state.code }
            : {};
    };

    handleCodeChange = new_code => event => {
        const val = event.target.value;
        if(val){ 
            this.setState({
                [new_code]: val
            });
        }else{
            this.setState({
                [new_code]: ""
            });
        }
    };    
  
    render(){
    return (
        <div id="wrapper">
            <HTMLComment text=" Menu" />
            <DashMenu />

            <div id="content-wrapper">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-6">
                            <DashTopBar />
                        </div>
                        <p class="col-lg-6">
                        <TextField
                            id="date_from"
                            label="From"
                            type="date"
                            value={this.state.from}
                            onChange={this.handleFromChange("from")}
                            defaultValue="2015-01-01"
                            className="flex wrap text-white"
                            InputLabelProps={{
                            shrink: true,
                            }}
                        />  
                        <TextField
                            id="date_to"
                            label="To"
                            type="date"
                            value={this.state.to}
                            onChange={this.handleFromChange("to")}
                            defaultValue="2019-08-09"
                            className="flex wrap text-white ml-1"
                            InputLabelProps={{
                            shrink: true,
                            }}
                        /> 
                        <TextField
                            id="code"
                            label="Code"
                            type="text"
                            value={this.props.code}
                            defaultValue="Z132"
                            className="flex wrap text-white ml-1 mr-1"
                            onChange={this.handleCodeChange("code")}
                        />
                        </p>
                    </div>

                    <CourseTypes code={this.state.code} />

                    <div class="card mt-5">
                        <div class="card-header bg-dark text-white">
                            <i class="fas fa-chart-area"></i>
                        Instructors
                        </div>
                        <div class="card-body">
                            <InstructorView code={this.state.code} from={this.state.from} to={this.state.to}/>
                        </div>
                        <div class="card-footer small text-muted">Updated yesterday at 11:59 PM</div>
                    </div>

                    <div class="card mt-5">
                        <div class="card-header bg-dark text-white">
                        <i class="fas fa-chart-area"></i>
                        Languages<span class="float-right">Learners per classification</span></div>
                        <div class="card-body">
                        <div class="row">
                            <div class="col-sm-8">
                                <Language code={this.state.code} from={this.state.from} to={this.state.to}/>
                            </div>
                            <div class="col-sm-4 text-right">
                                <ClassDept code={this.state.code} from={this.state.from} to={this.state.to}/>
                            </div>
                        </div>
                        </div>
                        <div class="card-footer small text-muted">Updated yesterday at 11:59 PM</div>
                    </div>


                    <div class="card mt-5">
                        <div class="card-header bg-dark text-white">
                            <i class="fas fa-chart-area"></i>
                        Learners per department
                        </div>
                        <div class="card-body d-flex justify-content-center">
                            <Learner code={this.state.code} from={this.state.from} to={this.state.to}/>
                        </div>
                        <div class="card-footer small text-muted">Updated yesterday at 11:59 PM</div>
                    </div>

                </div>
            </div>
        </div>
    );
    }
}

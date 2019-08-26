import React from 'react';
import HTMLComment from './HTMLComment'
import { Query } from "react-apollo";
import gql from "graphql-tag";
import { TextField, Card, CardContent, Typography, CardActions, Button, Grid } from '@material-ui/core';
import DashBreadcrumbs from './DashBreadcrumbs';
import ChoiceView from './ChoiceView';
import ClassifiedView from './ClassifiedView';
import FreeText from './FreeText';


export default class DashBoard extends React.Component{

  
  constructor(props) {
    super(props);

    this.state = {
      survey_id: "test_sur"
    };
  }

  

  getSurveyId = () => {
      return this.state.survey_id.length > 0
          ? { survey_id_contains: this.state.survey_id }
          : {};
  };

  handleSurveyIdChange = survey_id => event => {
      const val = event.target.value;
      if(val){ 
          this.setState({
              [survey_id]: val
          });
      }else{
          this.setState({
              [survey_id]: "test_sur"
          });
      }
  };
  
  render(){
    return (
      <Query
        query={gql`query offeringsRangeQuery(
                $sur_id: String
            ){
            all_survey_questions(sur_id:$sur_id){
              uid,
              answer_total,
              classified_as,
              question,
              stats,
              options,
              type
            }
          }
        `}
        variables={{
            sur_id: this.state.survey_id
        }}
        >
          {({ loading, error, data }) => {
            if (loading) return <p class="d-flex justify-content-center mt-5">Loading...</p>;

            if (error) return <p class="d-flex justify-content-center mt-5">Error</p>; 
            
            let total_answers = 0;
            let questionsData = [];
            
            for(let q of data.all_survey_questions){

              if(q.answer_total)
                total_answers++;

              let json_stats = JSON.parse(q.stats)
              let q_stats = []

              for(let i in json_stats)
                q_stats.push({name:i, value:json_stats[i]});

              questionsData.push({uid: q.uid, answer_total: q.answer_total, question: q.question[0], type: q.type, classified_as: q.classified_as, stats: q_stats});
            }
          
            return (
              <div id="wrapper">
                <HTMLComment text="Menu" />

                <div id="content-wrapper" class="ml-3 mr-3">
                    <div class="row">
                      <DashBreadcrumbs className="col-lg-9"/>
                      <p class="col-lg-3"> 
                        <TextField
                            id="date"
                            label="Survey id"
                            type="text"
                            value={this.state.survey_id}
                            onChange={this.handleSurveyIdChange("survey_id")}
                            className="flex wrap text-white ml-1"
                            InputLabelProps={{
                            shrink: true,
                            }}
                        />
                      </p>
                    </div>

                    <div class="row">
                      <div class="col-xl-6 col-sm-6 mb-3">
                        <div class="card text-white bg-primary o-hidden h-100">
                          <div class="card-body">
                            <div class="card-body-icon">
                              <i class="fas fa-fw fa-comments"></i>
                            </div>
                            <div class="mr-5">{data.all_survey_questions.length} Questions</div>
                          </div>
                          <a class="card-footer text-white clearfix small z-1" href="#">
                            <span class="float-left">View Details</span>
                            <span class="float-right">
                              <i class="fas fa-angle-right"></i>
                            </span>
                          </a>
                        </div>
                      </div>

                      <div class="col-xl-6 col-sm-6 mb-3">
                        <div class="card text-white bg-success o-hidden h-100">
                          <div class="card-body">
                            <div class="card-body-icon">
                              <i class="fas fa-fw fa-comments"></i>
                            </div>
                            <div class="mr-5">{total_answers} Answers</div>
                          </div>
                          <a class="card-footer text-white clearfix small z-1" href="#">
                            <span class="float-left">View Details</span>
                            <span class="float-right">
                              <i class="fas fa-angle-right"></i>
                            </span>
                          </a>
                        </div>
                      </div>
                    </div>

                    <span class="mb-3"></span>

                    <p class="lead">Single / Multi choice</p>

                    <Grid container spacing={3}>
                      {questionsData.map(n => {
                        if(n.type === "SINGLE_CHOICE" || n.type === "MULTI_CHOICE"){
                          return (
                            <Grid item xs={3}>
                              <Card key={n.uid}>
                                <CardContent>
                                  <Typography variant="h5" component="h2">
                                    {n.question}
                                  </Typography>
                                  <Typography color="textSecondary">
                                    {n.type}
                                  </Typography>
                                  <Typography variant="body2" component="p">
                                    <ChoiceView data={n.stats} />
                                  </Typography>
                                </CardContent>
                                <CardActions>
                                  <Button size="small">View details</Button>
                                </CardActions>
                              </Card>
                            </Grid>
                          );
                        }
                      })}
                    </Grid>

                    <p class="lead mt-3">Free text</p>

                    <Grid container spacing={5}>
                      {questionsData.map(n => {
                        if(n.type === "FREE_TEXT"){
                          return (
                            <Grid item xs={3}>
                              <Card key={n.uid}>
                                <CardContent>
                                  <Typography variant="h5" component="h2">
                                    {n.question}
                                  </Typography>
                                  <Typography color="textSecondary">
                                    {n.type}
                                  </Typography>

                                  <Typography variant="body2" component="p">
                                    <FreeText data={n.stats} />
                                  </Typography>
                                </CardContent>
                                <CardActions>
                                  <Button size="small" color="textPrimary">View details</Button>
                                </CardActions>
                              </Card>
                            </Grid>
                          );
                        }
                      })}
                    </Grid>

                    <p class="lead mt-3">Classified</p>

                    <Grid container spacing={3} mt={3}>
                      {questionsData.map(n => {
                        if(n.type === "CLASSIFIED"){
                          return (
                            <Grid item xs={4}>
                              <Card key={n.uid}>
                                <CardContent>
                                  <Typography variant="h5" component="h2">
                                    {n.question}
                                  </Typography>
                                  <Typography color="textSecondary">
                                    {n.type}
                                  </Typography>

                                  <Typography variant="body2" component="p">
                                    <ClassifiedView data={n.stats} />
                                  </Typography>
                                </CardContent>
                                <CardActions>
                                  <Button size="small" color="textPrimary">View details</Button>
                                </CardActions>
                              </Card>
                            </Grid>
                          );
                        }
                      })}
                    </Grid>

                  </div>
                </div>
            )}}
      </Query>
    );
  }
}

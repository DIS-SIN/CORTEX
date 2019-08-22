import React from 'react';
import HTMLComment from './HTMLComment'

export default class RetinaFooter extends React.Component{
  
    render(){
        return (
            <div>
                <HTMLComment text="Footer" />
                <footer class="sticky-footer bg-white">
                    <div class="container my-auto">
                    <div class="copyright text-center my-auto">
                        <span>Copyright &copy; Retina</span>
                    </div>
                    </div>
                </footer>
                <HTMLComment text="End of Footer" />
            </div>
        );
    }
}
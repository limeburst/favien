/** @jsx React.DOM */

var requests = [];
var evtSource = new EventSource('stream/');

evtSource.addEventListener('collaboration-request', function(e) {
    var data = JSON.parse(e.data);
    if (requests.indexOf(data.screen_name) === -1) {
        requests.push(data.screen_name);
    }
    React.render(
        <CollaborationRequestList requests={requests} />,
        document.getElementById('collaboration-requests')
    );
});

evtSource.addEventListener('strokes', function(e) {
    var data = $.parseJSON(e.data);
    strokes = data.strokes;
    while (strokes.length) {
        replayStroke($('#drawing-canvas'))
    }
});

var ProfileLink = React.createClass({
    render: function() {
        return (
            <a href={'/' + this.props.screen_name + '/'}>
                {this.props.screen_name}
            </a>
        );
    }
});

var CollaborationRequest = React.createClass({
    render: function() {
        return (
            <tr>
                <td>
                    <CollaborationRequestCheckbox screen_name={this.props.screen_name} />
                </td>
                <td>
                    <ProfileLink screen_name={this.props.screen_name} />
                </td>
            </tr>
        );
    }
});

var CollaborationRequestList = React.createClass({
    render: function() {
        var rows = [];
        this.props.requests.forEach(function(screen_name) {
            rows.push(
                <CollaborationRequest key={screen_name} screen_name={screen_name} />
            );
        });
        return (
            <table>{rows}</table>
        );
    }
});

var CollaborationRequestCheckbox = React.createClass({
    getInitialState: function() {
        return {disabled: false}
    },
    handleClick: function() {
        console.log(this);
        $.post('collaborators/', {collaborator: this.props.screen_name},
            function() {
                this.setState({disabled: true});
            }.bind(this)
        );
    },
    render: function() {
        return (
            <input type="checkbox" onClick={this.handleClick} disabled={this.state.disabled} />
        )
    }
});

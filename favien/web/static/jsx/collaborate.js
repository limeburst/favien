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
            <li>
                <ProfileLink screen_name={this.props.screen_name} />
            </li>
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
            <ul>{rows}</ul>
        );
    }
});

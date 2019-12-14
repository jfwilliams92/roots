import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly
import plotly.graph_objs as go 
import json

from treecreation import create_tree
from treeplotting import plotly_graph

tree = create_tree()
tree.update_node_positions()
selected_nodes = []

fig = plotly_graph(tree._graph)

DEFAULT_COLOR = 'blue'
DEFAULT_SIZE = 10

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    children=[
    html.H1(children='Hello Dash'),

    html.Div(
        children='''
        Dash: A web application framework for Python.
        '''
    ),

    html.Div(
        className="row",
        children = [
            dcc.Graph(
                id='example-graph',
                figure=fig
            ),

            html.Div(
                id='text-output',
                children='Click a point on the graph to change me'
            )   
        ]
    ),

    html.Div(
        className="row",
        children=[
            html.Div(
                id="node-1", children="", className="five columns"
            ),
            html.Div(
                id="relationship", children="", className="two columns"
            ),
            html.Div(
                id="node-2", children="", className="five columns"
            )
        ]
    )   
])

def retrieve_node_data(tree, node_idx):
    return tree._graph.nodes[node_idx]


@app.callback(
    [
        Output('text-output', 'children'),
        Output('example-graph', 'figure'),
        Output('node-1', 'children'),
        Output('relationship', 'children'),
        Output('node-2', 'children')
    ],
    [Input('example-graph', 'clickData')],
    [State('example-graph', 'figure')]
    )
def display_click_data(clickData, fig):
    relationship = ""
    if clickData is not None:
        point_data = clickData['points'][0]['pointIndex']

        if len(selected_nodes) == 0:
            selected_nodes.append(point_data)

        elif len(selected_nodes) > 0:
            if point_data in selected_nodes:
                selected_nodes.remove(point_data)
                fig['data'][1]['marker']['color'][point_data] = 'blue'
                fig['data'][1]['marker']['size'][point_data] = 10

            else:
                # point is not in selected points already
                if len(selected_nodes) < 2:
                    selected_nodes.append(point_data)

                elif len(selected_nodes) == 2:
                    removed_point_idx = selected_nodes[0]
                    fig['data'][1]['marker']['color'][removed_point_idx] = 'blue'
                    fig['data'][1]['marker']['size'][removed_point_idx] = 10

                    selected_nodes[0] = selected_nodes[1]
                    selected_nodes[1] = point_data

                relationship = tree.determine_familial_relationship(selected_nodes[0] + 1, selected_nodes[1] + 1)
                
    node_data = ["", ""]
    for idx, point_idx in enumerate(selected_nodes):
        node_data[idx] = json.dumps(
            tree._graph.nodes[point_idx + 1],
            default=lambda x: 'not working',
            indent=4
        )
        #print(tree._graph.nodes[point_idx + 1])
        fig['data'][1]['marker']['color'][point_idx] = 'red'
        fig['data'][1]['marker']['size'][point_idx] = 12

    selected_nodes_str = [str(d) for d in selected_nodes]
    selected_nodes_str = '; '.join(selected_nodes_str)

    return selected_nodes_str, fig, node_data[0], relationship, node_data[1]
    #return json.dumps(fig['data'][1])

if __name__ == '__main__':
    app.run_server(debug=True)
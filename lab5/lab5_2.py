import numpy as np
from dash import Dash, dcc, html, Input, Output, State, callback_context
import plotly.graph_objs as go

app = Dash(__name__, suppress_callback_exceptions=True)

DEFAULT_AMPLITUDE = 1.0
DEFAULT_FREQUENCY = 1.0
DEFAULT_PHASE = 0.0
DEFAULT_NOISE_LEVEL = 0.0
DEFAULT_NOISE_VARIANCE = 0.1
DEFAULT_CUTOFF_FREQUENCY = 0.1
SHOW_NOISE_DEFAULT = True
RANDOM_NOISE = np.random.normal(0, 1, 1000)

def generate_harmonic(amplitude, frequency, phase, noise_level, noise_variance, display_noise=True):
    t = np.linspace(0, 10, 1000)
    harmonic_signal = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    if display_noise:
        noise = noise_level + np.sqrt(noise_variance) * RANDOM_NOISE
        harmonic_signal += noise
    return t, harmonic_signal

def apply_highpass_filter(input_signal, cutoff_frequency=0.1):
    filtered_signal = np.zeros_like(input_signal)
    for i in range(1, len(input_signal)):
        filtered_signal[i] = input_signal[i] - cutoff_frequency * input_signal[i-1]
    return filtered_signal

app.layout = html.Div([
    html.Div([
        dcc.Graph(id='original-graph'),
    ], id='original-graph-div', style={'width': '48%', 'height': '400px', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='filtered-graph'),
    ], id='filtered-graph-div', style={'width': '48%', 'height': '400px', 'display': 'inline-block'}),
    html.Div([
        html.Label('Select Parameter'),
        dcc.Dropdown(
            id='parameter-dropdown',
            options=[
                {'label': 'Amplitude', 'value': 'amplitude'},
                {'label': 'Frequency', 'value': 'frequency'},
                {'label': 'Phase', 'value': 'phase'},
                {'label': 'Noise (Mean)', 'value': 'noise_level'},
                {'label': 'Noise (Dispersion)', 'value': 'noise_variance'},
                {'label': 'Cutoff Frequency for Highpass Filter', 'value': 'cutoff_frequency'}
            ],
            value='amplitude'
        ),
    ]),
    html.Div([
        dcc.Slider(id='parameter-slider', min=0, max=5, step=0.1, value=DEFAULT_AMPLITUDE, marks={i: str(i) for i in range(6)})
    ], id='slider-container'),
    dcc.Checklist(id='show-noise-checkbox', options=[{'label': 'Show Noise', 'value': 'show_noise'}], value=['show_noise']),
    html.Div([
        html.Button('Reset', id='reset-button', n_clicks=0, style={'margin-right': '10px'}),
        html.Button('New Noise', id='new-noise-button', n_clicks=0)
    ], style={'margin-bottom': '20px'}),
    html.Label('Original Graph Width (%)'),
    dcc.Slider(id='original-width-slider', min=10, max=100, step=1, value=48, marks={i: str(i) for i in range(10, 101, 10)}),
    html.Label('Original Graph Height (px)'),
    dcc.Slider(id='original-height-slider', min=100, max=800, step=10, value=400, marks={i: str(i) for i in range(100, 801, 100)}),
    html.Label('Filtered Graph Width (%)'),
    dcc.Slider(id='filtered-width-slider', min=10, max=100, step=1, value=48, marks={i: str(i) for i in range(10, 101, 10)}),
    html.Label('Filtered Graph Height (px)'),
    dcc.Slider(id='filtered-height-slider', min=100, max=800, step=10, value=400, marks={i: str(i) for i in range(100, 801, 100)}),
])

@app.callback(
    [Output('original-graph-div', 'style'),
     Output('filtered-graph-div', 'style'),
     Output('original-graph', 'figure'),
     Output('filtered-graph', 'figure')],
    [Input('original-width-slider', 'value'),
     Input('original-height-slider', 'value'),
     Input('filtered-width-slider', 'value'),
     Input('filtered-height-slider', 'value'),
     Input('parameter-dropdown', 'value'),
     Input('parameter-slider', 'value'),
     Input('show-noise-checkbox', 'value'),
     Input('new-noise-button', 'n_clicks'),
     Input('reset-button', 'n_clicks')]
)
def update_graph_sizes_and_plots(original_width, original_height, filtered_width, filtered_height, parameter, value, show_noise, new_noise_clicks, reset_clicks):
    ctx = callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'new-noise-button':
        global RANDOM_NOISE
        RANDOM_NOISE = np.random.normal(0, 1, 1000)

    if button_id == 'reset-button':
        return [
            {'width': '48%', 'height': '400px', 'display': 'inline-block'},
            {'width': '48%', 'height': '400px', 'display': 'inline-block'},
            {'data': [], 'layout': go.Layout(title='Harmonic Signal with Noise', xaxis={'title': 'Time'}, yaxis={'title': 'Amplitude'})},
            {'data': [], 'layout': go.Layout(title='Filtered Signal', xaxis={'title': 'Time'}, yaxis={'title': 'Amplitude'})}
        ]

    amplitude = DEFAULT_AMPLITUDE
    frequency = DEFAULT_FREQUENCY
    phase = DEFAULT_PHASE
    noise_level = DEFAULT_NOISE_LEVEL
    noise_variance = DEFAULT_NOISE_VARIANCE
    cutoff_frequency = DEFAULT_CUTOFF_FREQUENCY

    if parameter == 'amplitude':
        amplitude = value
    elif parameter == 'frequency':
        frequency = value
    elif parameter == 'phase':
        phase = value
    elif parameter == 'noise_level':
        noise_level = value
    elif parameter == 'noise_variance':
        noise_variance = value
    elif parameter == 'cutoff_frequency':
        cutoff_frequency = value

    t, harmonic_output = generate_harmonic(amplitude, frequency, phase, noise_level, noise_variance, 'show_noise' in show_noise)
    filtered_output = apply_highpass_filter(harmonic_output, cutoff_frequency)

    original_figure = {
        'data': [{'x': t, 'y': harmonic_output, 'type': 'line', 'name': 'Harmonic Signal'}],
        'layout': go.Layout(
            title='Harmonic Signal with Noise',
            xaxis={'title': 'Time'},
            yaxis={'title': 'Amplitude'},
            height=original_height
        )
    }

    filtered_figure = {
        'data': [{'x': t, 'y': filtered_output, 'type': 'line', 'name': 'Filtered Signal', 'line': {'color': 'orange'}}],
        'layout': go.Layout(
            title='Filtered Signal',
            xaxis={'title': 'Time'},
            yaxis={'title': 'Amplitude'},
            height=filtered_height
        )
    }

    original_style = {'width': f'{original_width}%', 'height': f'{original_height}px', 'display': 'inline-block'}
    filtered_style = {'width': f'{filtered_width}%', 'height': f'{filtered_height}px', 'display': 'inline-block'}

    return original_style, filtered_style, original_figure, filtered_figure

@app.callback(
    Output('slider-container', 'children'),
    [Input('parameter-dropdown', 'value')]
)
def update_slider(parameter):
    if parameter == 'amplitude':
        return dcc.Slider(id='parameter-slider', min=0.1, max=5.0, step=0.1, value=DEFAULT_AMPLITUDE, marks={i: str(i) for i in range(1, 6)})
    elif parameter == 'frequency':
        return dcc.Slider(id='parameter-slider', min=0.1, max=5.0, step=0.1, value=DEFAULT_FREQUENCY, marks={i: str(i) for i in range(1, 6)})
    elif parameter == 'phase':
        return dcc.Slider(id='parameter-slider', min=-np.pi, max=np.pi, step=0.1, value=DEFAULT_PHASE, marks={-np.pi: '-π', 0: '0', np.pi: 'π'})
    elif parameter == 'noise_level':
        return dcc.Slider(id='parameter-slider', min=-1.0, max=1.0, step=0.1, value=DEFAULT_NOISE_LEVEL, marks={i: str(i) for i in np.arange(-1, 1.1, 0.5)})
    elif parameter == 'noise_variance':
        return dcc.Slider(id='parameter-slider', min=0.01, max=1.0, step=0.01, value=DEFAULT_NOISE_VARIANCE, marks={i: str(i) for i in np.arange(0.01, 1.1, 0.2)})
    elif parameter == 'cutoff_frequency':
        return dcc.Slider(id='parameter-slider', min=0.01, max=1.0, step=0.01, value=DEFAULT_CUTOFF_FREQUENCY, marks={i: str(i) for i in np.arange(0.01, 1.1, 0.2)})

if __name__ == '__main__':
    app.run_server(debug=True, port=8052)


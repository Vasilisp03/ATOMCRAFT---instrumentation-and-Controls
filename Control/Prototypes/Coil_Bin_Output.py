import serial
import struct
import plotly.graph_objects as go

# UART Configuration
PORT = "COM3"         # Change this to your serial port
BAUDRATE = 115200     # Match FPGA settings
TIMEOUT = 10          # Timeout (enough to receive full file)

def receive_bin_from_serial(port, baudrate, timeout):
    """Receives .bin data from FPGA over UART."""
    with serial.Serial(port, baudrate, timeout=timeout) as ser:
        print("Waiting for binary file dump...")
        
        # Read all available incoming data
        data = ser.read_all()

        if not data:
            raise Exception("No data received from serial port!")
        
        print(f"Received {len(data)} bytes from FPGA.")
        return data

def decode_data(raw_data):
    """Decode raw binary data into list of current values."""
    SAMPLE_SIZE = 2  # 16-bit integers
    num_samples = len(raw_data) // SAMPLE_SIZE
    current_values = list(struct.unpack(f"<{num_samples}h", raw_data))
    return current_values

def plot_data(current_values):
    """Plots the current data interactively using Plotly."""
    num_samples = len(current_values)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(range(num_samples)),
        y=current_values,
        mode='lines',
        name='Current (mA)'
    ))

    fig.update_layout(
        title="Current Measurements from FPGA (UART -> Plot)",
        xaxis_title="Sample #",
        yaxis_title="Current (mA)",
        hovermode="x unified",
        dragmode='pan',
    )

    fig.show()

# --- Main program ---
if __name__ == "__main__":
    try:
        raw_data = receive_bin_from_serial(PORT, BAUDRATE, TIMEOUT)
        current_values = decode_data(raw_data)
        plot_data(current_values)
    except Exception as e:
        print(f"Error: {e}")
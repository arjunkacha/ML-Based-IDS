import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_system_diagram():
    """Generate a comprehensive system diagram for the ML-Based IDS project"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Color scheme
    colors = {
        'data': '#E3F2FD',
        'preprocessing': '#FFF3E0', 
        'ml': '#E8F5E8',
        'interface': '#F3E5F5',
        'security': '#FFEBEE',
        'storage': '#F1F8E9'
    }
    
    # Title
    ax.text(5, 9.5, 'ML-Based Hybrid Intrusion Detection System', 
            fontsize=18, fontweight='bold', ha='center')
    
    # Data Layer
    data_box = FancyBboxPatch((0.5, 7.5), 2, 1.2, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['data'], 
                              edgecolor='black', linewidth=1.5)
    ax.add_patch(data_box)
    ax.text(1.5, 8.3, 'Data Sources', fontweight='bold', ha='center', fontsize=11)
    ax.text(1.5, 8.0, '• CICIDS2017 Dataset', ha='center', fontsize=9)
    ax.text(1.5, 7.8, '• Live Network Traffic', ha='center', fontsize=9)
    ax.text(1.5, 7.6, '• UDP Flood Generator', ha='center', fontsize=9)
    
    # Data Preprocessing
    preprocess_box = FancyBboxPatch((3.5, 7.5), 2, 1.2,
                                   boxstyle="round,pad=0.1",
                                   facecolor=colors['preprocessing'],
                                   edgecolor='black', linewidth=1.5)
    ax.add_patch(preprocess_box)
    ax.text(4.5, 8.3, 'Data Preprocessing', fontweight='bold', ha='center', fontsize=11)
    ax.text(4.5, 8.0, '• Feature Extraction', ha='center', fontsize=9)
    ax.text(4.5, 7.8, '• Normalization', ha='center', fontsize=9)
    ax.text(4.5, 7.6, '• Label Encoding', ha='center', fontsize=9)
    
    # ML Models
    ml_box = FancyBboxPatch((6.5, 7.5), 2.5, 1.2,
                           boxstyle="round,pad=0.1",
                           facecolor=colors['ml'],
                           edgecolor='black', linewidth=1.5)
    ax.add_patch(ml_box)
    ax.text(7.75, 8.3, 'ML Models', fontweight='bold', ha='center', fontsize=11)
    ax.text(7.75, 8.0, '• Random Forest (Supervised)', ha='center', fontsize=9)
    ax.text(7.75, 7.8, '• Isolation Forest (Unsupervised)', ha='center', fontsize=9)
    ax.text(7.75, 7.6, '• Decision Tree', ha='center', fontsize=9)
    
    # Core Processing Engine
    engine_box = FancyBboxPatch((2, 5.5), 6, 1.5,
                               boxstyle="round,pad=0.1",
                               facecolor=colors['security'],
                               edgecolor='black', linewidth=2)
    ax.add_patch(engine_box)
    ax.text(5, 6.6, 'Hybrid IDS Engine', fontweight='bold', ha='center', fontsize=14)
    ax.text(3.5, 6.2, '• Real-time Packet Analysis', ha='left', fontsize=10)
    ax.text(3.5, 6.0, '• Known Attack Detection', ha='left', fontsize=10)
    ax.text(3.5, 5.8, '• Anomaly Detection', ha='left', fontsize=10)
    ax.text(6.5, 6.2, '• Alert Generation', ha='left', fontsize=10)
    ax.text(6.5, 6.0, '• Threat Classification', ha='left', fontsize=10)
    ax.text(6.5, 5.8, '• Performance Monitoring', ha='left', fontsize=10)
    
    # User Interface Layer
    ui_box1 = FancyBboxPatch((0.5, 3.5), 2.8, 1.2,
                            boxstyle="round,pad=0.1",
                            facecolor=colors['interface'],
                            edgecolor='black', linewidth=1.5)
    ax.add_patch(ui_box1)
    ax.text(1.9, 4.3, 'File Analysis Interface', fontweight='bold', ha='center', fontsize=11)
    ax.text(1.9, 4.0, '• CSV Upload', ha='center', fontsize=9)
    ax.text(1.9, 3.8, '• Batch Processing', ha='center', fontsize=9)
    ax.text(1.9, 3.6, '• Results Visualization', ha='center', fontsize=9)
    
    ui_box2 = FancyBboxPatch((3.6, 3.5), 2.8, 1.2,
                            boxstyle="round,pad=0.1",
                            facecolor=colors['interface'],
                            edgecolor='black', linewidth=1.5)
    ax.add_patch(ui_box2)
    ax.text(5, 4.3, 'Live Analysis Interface', fontweight='bold', ha='center', fontsize=11)
    ax.text(5, 4.0, '• Real-time Monitoring', ha='center', fontsize=9)
    ax.text(5, 3.8, '• Live Alerts', ha='center', fontsize=9)
    ax.text(5, 3.6, '• Network Sniffing', ha='center', fontsize=9)
    
    ui_box3 = FancyBboxPatch((6.7, 3.5), 2.8, 1.2,
                            boxstyle="round,pad=0.1",
                            facecolor=colors['interface'],
                            edgecolor='black', linewidth=1.5)
    ax.add_patch(ui_box3)
    ax.text(8.1, 4.3, 'Performance Dashboard', fontweight='bold', ha='center', fontsize=11)
    ax.text(8.1, 4.0, '• Model Metrics', ha='center', fontsize=9)
    ax.text(8.1, 3.8, '• Confusion Matrix', ha='center', fontsize=9)
    ax.text(8.1, 3.6, '• Accuracy Reports', ha='center', fontsize=9)
    
    # Storage Layer
    storage_box = FancyBboxPatch((2, 1.5), 6, 1.2,
                                boxstyle="round,pad=0.1",
                                facecolor=colors['storage'],
                                edgecolor='black', linewidth=1.5)
    ax.add_patch(storage_box)
    ax.text(5, 2.3, 'Model & Data Storage', fontweight='bold', ha='center', fontsize=12)
    ax.text(3, 2.0, '• Trained Models (.pkl)', ha='left', fontsize=10)
    ax.text(3, 1.8, '• Preprocessors (scaler, encoder)', ha='left', fontsize=10)
    ax.text(6, 2.0, '• Alert Logs (CSV)', ha='left', fontsize=10)
    ax.text(6, 1.8, '• Training Data', ha='left', fontsize=10)
    
    # Attack Simulation
    attack_box = FancyBboxPatch((0.5, 0.2), 2, 0.8,
                               boxstyle="round,pad=0.1",
                               facecolor='#FFCDD2',
                               edgecolor='red', linewidth=1.5)
    ax.add_patch(attack_box)
    ax.text(1.5, 0.7, 'Attack Simulation', fontweight='bold', ha='center', fontsize=10)
    ax.text(1.5, 0.4, 'UDP Flooder', ha='center', fontsize=9)
    
    # Network Interface
    network_box = FancyBboxPatch((7.5, 0.2), 2, 0.8,
                                boxstyle="round,pad=0.1",
                                facecolor='#E1F5FE',
                                edgecolor='blue', linewidth=1.5)
    ax.add_patch(network_box)
    ax.text(8.5, 0.7, 'Network Interface', fontweight='bold', ha='center', fontsize=10)
    ax.text(8.5, 0.4, 'Scapy Packet Capture', ha='center', fontsize=9)
    
    # Arrows - Data Flow
    # Data to Preprocessing
    arrow1 = ConnectionPatch((2.5, 8.1), (3.5, 8.1), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5, 
                           mutation_scale=20, fc="black")
    ax.add_patch(arrow1)
    
    # Preprocessing to ML
    arrow2 = ConnectionPatch((5.5, 8.1), (6.5, 8.1), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5,
                           mutation_scale=20, fc="black")
    ax.add_patch(arrow2)
    
    # ML to Engine
    arrow3 = ConnectionPatch((7.75, 7.5), (5, 7.0), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5,
                           mutation_scale=20, fc="black")
    ax.add_patch(arrow3)
    
    # Engine to UI
    arrow4 = ConnectionPatch((3.5, 5.5), (1.9, 4.7), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5,
                           mutation_scale=20, fc="black")
    ax.add_patch(arrow4)
    
    arrow5 = ConnectionPatch((5, 5.5), (5, 4.7), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5,
                           mutation_scale=20, fc="black")
    ax.add_patch(arrow5)
    
    arrow6 = ConnectionPatch((6.5, 5.5), (8.1, 4.7), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5,
                           mutation_scale=20, fc="black")
    ax.add_patch(arrow6)
    
    # Engine to Storage
    arrow7 = ConnectionPatch((5, 5.5), (5, 2.7), "data", "data",
                           arrowstyle="<->", shrinkA=5, shrinkB=5,
                           mutation_scale=20, fc="black")
    ax.add_patch(arrow7)
    
    # Attack simulation to Engine
    arrow8 = ConnectionPatch((2.5, 0.6), (3, 5.5), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5,
                           mutation_scale=20, fc="red")
    ax.add_patch(arrow8)
    
    # Network to Engine
    arrow9 = ConnectionPatch((7.5, 0.6), (7, 5.5), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5,
                           mutation_scale=20, fc="blue")
    ax.add_patch(arrow9)
    
    # Legend
    legend_elements = [
        patches.Patch(color=colors['data'], label='Data Layer'),
        patches.Patch(color=colors['preprocessing'], label='Preprocessing'),
        patches.Patch(color=colors['ml'], label='Machine Learning'),
        patches.Patch(color=colors['security'], label='Security Engine'),
        patches.Patch(color=colors['interface'], label='User Interface'),
        patches.Patch(color=colors['storage'], label='Storage')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    plt.tight_layout()
    plt.savefig('ML_IDS_System_Diagram.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    create_system_diagram()
    print("System diagram generated and saved as 'ML_IDS_System_Diagram.png'")
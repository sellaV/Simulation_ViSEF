import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import ipywidgets as widgets
from ipywidgets import interactive, VBox, HBox, Output
from IPython.display import display  # <<< DÒNG NÀY ĐÃ ĐƯỢC THÊM VÀO

# --- DÁN LẠI TẤT CẢ CÁC HÀM CŨ CỦA CHÚNG TA ---

def tao_dom_gaussian(ma_tran, vi_tri, cuong_do, do_rong):
    """
    Vẽ một "đốm sáng" Gaussian 2D lên ma trận tại một vị trí.
    """
    k_thuoc = ma_tran.shape[0]
    y, x = vi_tri
    ys, xs = np.ogrid[:k_thuoc, :k_thuoc]
    
    khoang_cach_binh_phuong = (xs - x)**2 + (ys - y)**2
    dom_sang = cuong_do * np.exp(-khoang_cach_binh_phuong / (2 * do_rong**2))
    
    ma_tran += dom_sang
    return ma_tran

def gia_lap_ban_do_tinh(goc_MCP, goc_PIP, goc_DIP, k_thuoc=8):
    """
    Giả lập bản đồ áp suất 8x8 TĨNH dựa trên 3 góc gập.
    """
    ban_do = np.zeros((k_thuoc, k_thuoc))
    
    # Giả lập vị trí các khớp dựa trên góc
    y_MCP = 6
    x_MCP = 4
    vi_tri_MCP = (y_MCP, x_MCP) 
    tao_dom_gaussian(ban_do, vi_tri_MCP, cuong_do=0.8, do_rong=1.5)
    
    y_PIP = y_MCP - (goc_MCP / 90.0) * 2.0 
    x_PIP = x_MCP
    vi_tri_PIP = (y_PIP, x_PIP)
    tao_dom_gaussian(ban_do, vi_tri_PIP, cuong_do=1.0, do_rong=1.2)
    
    y_DIP = y_PIP - (goc_PIP / 90.0) * 2.0
    x_DIP = x_PIP
    vi_tri_DIP = (y_DIP, x_DIP)
    tao_dom_gaussian(ban_do, vi_tri_DIP, cuong_do=0.7, do_rong=1.0)
    
    nhieu = np.random.rand(k_thuoc, k_thuoc) * 0.1
    ban_do += nhieu
    
    if ban_do.max() > 0:
        ban_do = ban_do / ban_do.max()
        
    return ban_do

def ve_khung_xuong_3d(ax, goc_MCP, goc_PIP, goc_DIP, mau='b', label=''):
    """
    Vẽ một mô hình khung xương 3D đơn giản của ngón tay.
    """
    L1 = 3 # Đốt gần (MCP -> PIP)
    L2 = 2 # Đốt giữa (PIP -> DIP)
    L3 = 1 # Đốt xa (DIP -> Đầu ngón)
    
    rad_MCP = np.deg2rad(goc_MCP)
    rad_PIP = np.deg2rad(goc_PIP)
    rad_DIP = np.deg2rad(goc_DIP)

    J0 = [0, 0, 0]
    
    J1_y = L1 * np.cos(rad_MCP)
    J1_z = L1 * np.sin(rad_MCP)
    J1 = [0, J1_y, J1_z]
    
    goc_tich_luy_PIP = rad_MCP + rad_PIP
    J2_y = J1[1] + L2 * np.cos(goc_tich_luy_PIP)
    J2_z = J1[2] + L2 * np.sin(goc_tich_luy_PIP)
    J2 = [0, J2_y, J2_z]
    
    goc_tich_luy_DIP = goc_tich_luy_PIP + rad_DIP
    Tip_y = J2[1] + L3 * np.cos(goc_tich_luy_DIP)
    Tip_z = J2[2] + L3 * np.sin(goc_tich_luy_DIP)
    Tip = [0, Tip_y, Tip_z]
    
    points = np.array([J0, J1, J2, Tip])
    
    ax.plot(points[:, 0], points[:, 1], points[:, 2], marker='o', color=mau, label=label)
    ax.set_xlabel('X')
    ax.set_ylabel('Y (Dọc ngón tay)')
    ax.set_zlabel('Z (Gập)')
    ax.set_title("Mô phỏng Mô hình Hóa Ngón tay 3D")
    ax.set_xlim([-1, 1])
    ax.set_ylim([0, 6])
    ax.set_zlim([0, 6])

# --- HÀM CẬP NHẬT GIAO DIỆN CHÍNH ---

def cap_nhat_giao_dien(goc_MCP, goc_PIP, goc_DIP):
    """
    Hàm này được gọi mỗi khi bạn kéo thanh trượt.
    Nó sẽ vẽ lại cả hai biểu đồ.
    """
    # 1. Tạo một khung hình mới với 2 ô (1 hàng, 2 cột)
    fig, (ax1, ax2_placeholder) = plt.subplots(1, 2, figsize=(12, 6))
    
    # --- Vẽ Ô 1: Bản đồ Áp suất Tĩnh ---
    ban_do_tinh = gia_lap_ban_do_tinh(goc_MCP, goc_PIP, goc_DIP)
    ax1.imshow(ban_do_tinh, cmap='viridis', vmin=0, vmax=1)
    ax1.set_title(f"Bản đồ Tĩnh (MCP={goc_MCP}°, PIP={goc_PIP}°)")
    ax1.set_xticks(np.arange(8))
    ax1.set_yticks(np.arange(8))

    # --- Vẽ Ô 2: Mô hình 3D ---
    # Phải xóa ô 2D cũ đi và tạo ô 3D mới
    fig.delaxes(ax2_placeholder)
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    
    # Vẽ ngón tay duỗi thẳng (để so sánh)
    ve_khung_xuong_3d(ax2, 0, 0, 0, mau='g', label='Duỗi thẳng (0°)')
    
    # Vẽ ngón tay co (theo thanh trượt)
    ve_khung_xuong_3d(ax2, goc_MCP, goc_PIP, goc_DIP, mau='r', label='Tư thế hiện tại')
    
    ax2.legend()
    
    # Hiển thị kết quả
    plt.tight_layout()
    plt.show()

# --- TẠO CÁC THANH TRƯỢT ---

# Tạo 3 thanh trượt, chạy từ 0 đến 90 độ, bước nhảy 1 độ
slider_MCP = widgets.IntSlider(value=30, min=0, max=90, step=1, description='Góc MCP:')
slider_PIP = widgets.IntSlider(value=50, min=0, max=90, step=1, description='Góc PIP:')
slider_DIP = widgets.IntSlider(value=10, min=0, max=90, step=1, description='Góc DIP:')

# Liên kết 3 thanh trượt với hàm `cap_nhat_giao_dien`
# interactive_output sẽ chứa các biểu đồ
interactive_output = interactive(cap_nhat_giao_dien, 
                                 goc_MCP=slider_MCP, 
                                 goc_PIP=slider_PIP, 
                                 goc_DIP=slider_DIP)

# Hiển thị giao diện: đặt các thanh trượt bên trên, biểu đồ bên dưới
display(VBox([HBox([slider_MCP, slider_PIP, slider_DIP]), interactive_output]))
# from app.prompts import SCENE_PROMPT, PHOTO_PROMPT


# print(PHOTO_PROMPT.format(current_scene=123,previous_frame_description=456))
a = 123
b = f"""
                请生成一幅手绘草图，风格要求：黑色线条勾勒，背景为纯白色，线条简洁清晰，无填充，无阴影，无颜色。  
                图像格式：JPG、JPEG、PNG、TIFF 或 WEBP。  
                图像分辨率：不小于 512×512 像素，不超过 1024×1024 像素。  
                绘制的主体是：{a}。"""

print(b)
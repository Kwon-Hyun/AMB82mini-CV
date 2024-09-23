**Requirements**
- OpenCV
- Python 3.9.7
Camera Calibration 예정

**기존 제공 dataset 결과**
<br>
![스크린샷 2024-09-23 오후 5 02 36](https://github.com/user-attachments/assets/0596f86c-34a7-4b33-a9fc-66c6697f453b)

<br>
<b>직접 촬영한 img data</b>
<br>
<img width="443" alt="스크린샷 2024-09-23 오후 6 19 26" src="https://github.com/user-attachments/assets/8390a348-36bb-4e67-8585-3f42cc6b59e4">

<br><br>

<b>해당 img data 복원 결과</b>
<br>
<img width="301" alt="스크린샷 2024-09-23 오후 6 17 08" src="https://github.com/user-attachments/assets/bac912cd-1277-41af-8749-75d8b8e1c696">

<br><br>
**terminal 상 위치 정보 제공 및 Dobot에서의 움직임 설명**
<br>
<img width="627" alt="스크린샷 2024-09-23 오후 6 18 36" src="https://github.com/user-attachments/assets/05bc24eb-ec98-4975-bbdb-f5d1e592cb14">

<br>
<b>한계점</b>
<br>
직접 촬영한 영상의 경우, cv 상에서 영상이 매우 느려짐을 확인할 수 있었음. 이 때문에 frame이 더 잘게 쪼개져 정확도가 떨어지는 경우가 발생함.
(frame 끊어짐은 내 예상..^^ ㅎㅎ 무튼 영상 속도를 조절해서 함 확인해 볼 필요성이 있음.)

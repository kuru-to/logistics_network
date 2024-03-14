# コード概観
## `optimizer.py`
### 最適化問題について
#### 決定変数
##### 拠点を開設するか否か
<img src="https://latex.codecogs.com/gif.latex?x_i\in\{0,1\}"/>

##### レーンを解説するか否か
<img src="https://latex.codecogs.com/gif.latex?y_{ij}\in\{0,1\}"/>

##### 拠点で生産される物量
<img src="https://latex.codecogs.com/gif.latex?p_i\geq{}0"/>

##### レーンijのk番目のコスト変化点まで物量が到達したか
<img src="https://latex.codecogs.com/gif.latex?z_{ijk}\in\{0,1\}"/>

##### レーンを通る物量. k番目からk+1番目までのコスト変化点の間
<img src="https://latex.codecogs.com/gif.latex?q_{ijk}\geq{}0"/>

#### 目的関数
<img src="https://latex.codecogs.com/gif.latex?\min_{x,y,z,p,q}(\sum_{i}(o_ix_i&plus;pc_ip_i)&plus;\sum_{i,j}(o_{ij}y_{ij}&plus;\sum_{k}c_{ijk}q_{ijk}))"/>

#### 制約条件
##### 拠点に入る物量と拠点から出ていく物量は等しい
<img src="https://latex.codecogs.com/gif.latex?\sum_{j,k}q_{jik}&plus;p_i=\sum_{j,k}q_{ijk}&plus;d_i"/>

##### 拠点が扱える物量を超えてはいけない
<img src="https://latex.codecogs.com/gif.latex?\sum_{j,k}q_{ijk}&plus;p_i\leq{}u_ix_i"/>

##### レーンが扱える物量を超えてはいけない
<img src="https://latex.codecogs.com/gif.latex?\sum_{k}q_{ijk}\leq{}u_{ij}y_{ij}"/>

##### コスト変化点間の物量を超えてはいけない
<img src="https://latex.codecogs.com/gif.latex?q_{ijk}\leq{}(s_{ijk}-s_{ij(k-1))})z_{ij(k-1)}"/>

##### 1つ前のコスト変化点まで物量が満たされていないとコストは変化しない
<img src="https://latex.codecogs.com/gif.latex?z_{ijk}\leq{}q_{ij(k-1)}/(s_{ijk}-s_{ij(k-1))})"/>

##### 小さい変化点から変化する
<img src="https://latex.codecogs.com/gif.latex?z_{ijk}\leq{}z_{ij(k-1)}"/>

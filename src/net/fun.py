#coding=gbk
'''
Created on 2013-4-25

@author: songjm
'''
import numpy as np
import scipy.signal as signal
def sigmoid(input):
    '激励函数'
    out=1.7159*np.tanh(2.0/3.0*input)
    return out
def dsigmoid(input):
    'sigmoid的导函数已知input=sigmod(out)'
    out=2.0/3.0/1.7159*(1.7159+input)*(1.7159-input)
    return out
def conv2d(fm,ct,kernel,bias):
    '卷积函数'
    "fm 特征图 三维"
    "ct 连接权矩阵"
    "kernel 卷积核 三维"
    "bias 偏置 向量"
    map_width=fm.shape[2]
    map_height=fm.shape[1]
    kernel_width=kernel.shape[2]
    kernel_height=kernel.shape[1]
    '计算特征图的尺寸'
    dst_height=map_height-kernel_height+1
    dst_width=map_width-kernel_width+1
    '计算输出特征图的数量'
    cfmDims=np.max(ct[1])+1
    n_kernels=kernel.shape[0]
    #print("ct's shape%d:%d"%(ct.shape[0],ct.shape[1]))
    ' 初始化结果特征图' 
    cfm=np.zeros((cfmDims,dst_height,dst_width))
    for index in xrange(0,cfmDims):
        "首先加上偏置值"
        cfm[index]+=bias[index]
    for index in xrange(0,n_kernels):
        #print(index)
        this_fm=fm[ct[0,index]]
        this_kernel=kernel[index]
        "计算卷积"
        this_conv=signal.convolve2d(this_fm, this_kernel, mode='valid')
        cfm_index=ct[1,index]
        cfm[cfm_index]+=this_conv
    "使用sigmoid压制"
    return sigmoid(cfm)
def subsampling(fm,sW,sb,pool_size,pool_stride):
    "重采样函数"
    "fm 特征图"
    "sW 重采样权值 向量"
    "sb 重采样偏置 向量"
    "pool_size 重采样窗口大小 二维矩阵"
    "pool_stride 步长 int"
    sfm_width=int((fm.shape[2]-pool_size[1])/pool_stride)+1
    sfm_height=int((fm.shape[1]-pool_size[0])/pool_stride)+1
    sfmDims=fm.shape[0]
    #sfm=np.zeros((sfmDims,sfm_width,sfm_height))
    sfm=[]
    "使用权值为1的核进行采样"
    kernel=np.ones(pool_size)
    for index in xrange(0,sfmDims):
        this_fm=fm[index]
        this_kernel=kernel*sW[index]
        "采样实际就是一次卷积过程"
        this_sfm=signal.convolve2d(this_fm, this_kernel, mode='valid')
        this_sfm=copy_fm(this_sfm,pool_stride)
        sfm.append(this_sfm)
    sfm=np.array(sfm)
    sfm=sigmoid(sfm)
    return sfm
def copy_fm(fm,stride):
    height=fm.shape[0]
    width=fm.shape[1]
    result=[]
    for y in xrange(0,height,stride):
        y_result=[]
        y_data=fm[y]
        for x in xrange(0,width,stride):
            y_result.append(y_data[x])
        result.append(y_result)
    return np.array(result)
def max_with_index(value):
    "返回最大值，及最大值的下标"
    "结果 [下标,最大值]"
    d=np.max(value)
    i=np.argmax(value)
    return [i,d]
def conv3d(input,w):
    out_height=input.shape[1]-w.shape[1]+1
    out_width=input.shape[2]-w.shape[2]+1
    out=np.zeros((out_height,out_width))
    for i in xrange(input.shape[0]):
        this_in=input[i]
        this_w=w[i]
        this_out=signal.convolve2d(this_in,this_w,mode='valid')
        out+=this_out
    return out
def dconv2_in(dout,input,kernel):
    return signal.convolve2d(dout,kernel,mode='full')
def dconv2_kernel(dout,input,kernel):
    return signal.convolve2d(input,dout,mode='valid')
def dconv3d(dout,din,input,w):
    din=np.zeros(input.shape)
    dw=np.zeros(w.shape)
    for i in xrange(input.shape[0]):
        this_in=input[i]
        this_w=w[i]
        this_din=dconv2_in(dout,this_in,this_w)
        din[i]=this_din
        this_dk=dconv2_kernel(dout,this_in,this_w)
        dw[i]=this_dk
    return [din,dw]
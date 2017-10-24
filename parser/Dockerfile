FROM ubuntu:16.04
 RUN apt-get update -y && apt-get install -y wget nano curl ca-certificates build-essential bzip2 libsm6 phantomjs xvfb && apt-get clean
 RUN mkdir /usr/src/log
 ADD environment.yml /
 ADD utils/entrypoint.py /
 ADD project/ /usr/src/app
 ENV CONDA_DIR /home/lenovo
 ENV MY_CONDA /home/lenovo/envs/test
 #ENTRYPOINT [ “/bin/bash”, “-c” ]
 RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-3.9.1-Linux-x86_64.sh && \
      /bin/bash /Miniconda3-3.9.1-Linux-x86_64.sh -b -p $CONDA_DIR && \
      rm Miniconda3-3.9.1-Linux-x86_64.sh && \
      $CONDA_DIR/bin/conda install --yes conda==4.3.24
 ENV PATH $CONDA_DIR/bin:$PATH
 #ENV PATH $CONDA_DIR/miniconda3/bin:$PATH
 RUN conda env create -f /environment.yml
 RUN conda env list && conda update conda -y
 RUN ["/bin/bash", "-c",  "source activate $MY_CONDA"]
 RUN apt-get update -y && apt-get install -y uwsgi-plugin-python3
 RUN mkdir /var/log/uwsgi
 RUN ["/bin/bash", "-c", "source activate $MY_CONDA &&  pip install uwsgi"]
 RUN chmod 777 /entrypoint.py
 WORKDIR /usr/src/app
 ENTRYPOINT ["/bin/bash", "-c", "source activate $MY_CONDA  &&  python /entrypoint.py"]

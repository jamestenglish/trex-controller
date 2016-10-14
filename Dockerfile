FROM python:2.7
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN echo "192.168.100.81      service-a-trex-demo-prod.router.default.svc.cluster.local service-b-trex-demo-prod.router.default.svc.cluster.local" >> /etc/hosts

EXPOSE 8080
ADD . /code
WORKDIR /code

RUN echo "192.168.100.81      service-a-trex-demo-prod.router.default.svc.cluster.local service-b-trex-demo-prod.router.default.svc.cluster.local" >> /etc/hosts && ls
CMD ["python", "app.py"]

FROM nginx

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/
#ENV PORTNGINX ${PORTNGINX}
#ENV PORTNGINX=${PORTNGINX}
#ENV PORTNGINX=${PORTNGINX}
#RUN sed -i s/PORTNGINX/${PORTNGINX}/g /etc/nginx/conf.d/nginx.conf

COPY --from=build /app/nginx.conf /etc/nginx/conf.d/default.conf

RUN cat /etc/nginx/conf.d/nginx.conf

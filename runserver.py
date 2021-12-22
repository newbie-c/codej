import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        'codej:app', host='127.0.0.1',
        reload=True, port=5000, log_level='info')

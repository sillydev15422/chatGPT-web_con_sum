import { useEffect, useRef, useState } from 'react';
import {
  CloudUploadOutlined,
  ClearOutlined,
  DeliveredProcedureOutlined,
  FormOutlined,
} from '@ant-design/icons';
import axios from 'axios';
import Papa from 'papaparse';
import {
  Input,
  Select,
  Card,
  Button,
  Row,
  Col,
  Divider,
  Space,
  Modal,
} from 'antd';
const { Option } = Select;
const { TextArea } = Input;

let index = 0;

function Landing() {
  const [items, setItems] = useState([]);
  const [name, setName] = useState('');
  const inputRef = useRef(null);
  const [open, setOpen] = useState(false);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [modalText, setModalText] = useState('Content of the modal');
  const [queText, setQueText] = useState('');
  const [csvFile, setCsvFile] = useState('');
  const [urlVal, setUrlVal] = useState('');
  const [answer, setAnswer] = useState('');
  const [sumar, setSum] = useState('');
  const onNameChange = (event) => {
    setName(event.target.value);
  };
  const addItem = (e) => {
    e.preventDefault();
    setItems([...items, name || `New item ${index++}`]);
    setName('');
    setTimeout(() => {
      inputRef.current?.focus();
    }, 0);
  };

  const showModal = () => {
    setOpen(true);
  };

  const getUrl = (e) => {
    setUrlVal(e.target.value);
  };
  const submitQue = () => {
    console.log(queText);
    axios
      .post('http://localhost:8000/getQuery', {
        data: queText,
      })
      .then((response) => {
        console.log(response.data.answer);
        setAnswer(response.data.answer);
      });
  };

  const handleOk = () => {
    setModalText('The modal will be closed after two seconds');
    setConfirmLoading(true);
    setTimeout(() => {
      setOpen(false);
      setConfirmLoading(false);
    }, 2000);
  };

  const clear = () => {
    setQueText(' ');
    setUrlVal(' ');
  };
  const create = () => {
    console.log(getUrl);
    axios
      .post('http://localhost:8000/getInput', { data: urlVal })
      .then((response) => {
        console.log(response.data);
        setSum(response.data.sum);
      });
  };

  const handleCancel = () => {
    console.log('Clicked cancel button');
    setOpen(false);
  };

  const handlechange = (e) => {
    setQueText(e.target.value);
  };

  const handleCsv = (e) => {
    const fileReader = new FileReader();
    if (e.target.files.length) {
      setCsvFile(e.target.files[0]);
      fileReader.onload = async ({ target }) => {
        const csv = Papa.parse(target.result, { header: true });
        const parsedData = csv?.data;
        for (var i = 0; i < parsedData.length - 1; i++) {
          console.log(parsedData[i].Link);
          axios
            .post('http://localhost:8000/getReply', {
              data: parsedData[i].Link,
            })
            .then((response) => {
              console.log(response);
            });
        }
      };
      fileReader.readAsText(e.target.files[0]);
    }
  };
  return (
    <>
      <Card style={{ height: '100%' }}>
        <Card className="card" title="Enter a webpage URL" bordered={true}>
          <div>
            <div
              style={{
                marginBottom: 16,
                display: 'flex',
                justifyContent: 'space-center',
              }}
            >
              <input
                type="file"
                accept={'.csv'}
                id="importCsv"
                onChange={handleCsv}
                style={{ display: 'none' }}
              ></input>
              <Input
                // addonBefore={selectBefore}
                // addonAfter={selectAfter}
                placeholder="https://openai.com/"
                onChange={getUrl}
                className="input"
              />
              <div style={{ paddingRight: 3 }}>
                <Button type="primary" onClick={create}>
                  <FormOutlined />
                  create
                </Button>
              </div>
              <div>
                <Button
                  type="primary"
                  onClick={() => {
                    document.getElementById('importCsv').click();
                  }}
                >
                  <CloudUploadOutlined />
                  Import
                </Button>
              </div>
            </div>
          </div>
        </Card>
        <Row>
          <Col span={8}>
            <Card
              className="card"
              title="Please leave your questions."
              bordered={true}
            >
              <TextArea
                showCount
                allowClear
                // readOnly
                maxLength={4500}
                rows={19}
                onChange={handlechange}
              />
            </Card>
            <div>
              <Button
                type="primary"
                style={{ width: '98%' }}
                className="button"
                onClick={clear}
              >
                <ClearOutlined />
                Clear
              </Button>
              <Button
                type="primary"
                style={{ width: '98%' }}
                className="button"
                onClick={submitQue}
              >
                <DeliveredProcedureOutlined />
                Submit
              </Button>
            </div>
          </Col>
          <Col span={16}>
            <Card title="Result" bordered={true} className="card">
              <TextArea showCount allowClear rows={10} value={answer} />
            </Card>
            <Card title="Summarize" bordered={true} className="card">
              <TextArea showCount allowClear rows={10} value={sumar} />
            </Card>
          </Col>
        </Row>
        {/* <Button type="primary" onClick={showModal} className="modalbutton">
          OpenAI_Key
        </Button>
        <Modal
          title="Insert OpenAI Key"
          open={open}
          onOk={handleOk}
          confirmLoading={confirmLoading}
          onCancel={handleCancel}
        >
          <Input placeholder="Input OpenAI Key" width={'100%'} required />
        </Modal> */}
      </Card>
    </>
  );
}

export default Landing;

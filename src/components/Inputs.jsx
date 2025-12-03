import './Inputs.css'

function Inputs ({ fileName, onFileNameChange, selectedValue, onSelectedValueChange }){

  return(
  <>
    <input 
      type="text" 
      placeholder="Enter the name of the file" 
      value={fileName}
      onChange={onFileNameChange}
    />
    <select 
      value={selectedValue} 
      onChange={onSelectedValueChange}
      className={selectedValue === 'bad' ? 'bad-select' : 'good-select'}
    >
      <option value="good">good</option>
      <option value="bad">bad</option>
    </select>
  </>) 
}

export default Inputs
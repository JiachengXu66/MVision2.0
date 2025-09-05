import { ChangeDetectionStrategy, ChangeDetectorRef, Component } from '@angular/core';
import { CreateTargetService } from './create-target.service';
import { Location, Person, Target } from 'src/shared/models/Entities';
import { Router } from '@angular/router';
@Component({
  selector: 'app-create-target',
  templateUrl: './create-target.component.html',
  styleUrls: ['./create-target.component.sass'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class CreateTargetComponent {
selectedTargetType: string = 'Choose Target Type';
submitStatus: boolean = false;
targetName: Target['target_name'] = '';
altName: Target['alt_name'] = '';

access: Location['access'] = null;
dobEntry: string = '';
role: Person['role'] = '';

constructor(private router: Router,
  private createTarget: CreateTargetService,
  private cdr: ChangeDetectorRef) { }

checkInputs()
{
  let errors: string[] = [];
  if (!this.targetName.trim()) {
    errors.push('Target Name must not be empty.');
  }
  if (!this.altName.trim()) {
    errors.push('Alt Name must not be empty.');
  }
  if (this.selectedTargetType === 'Location') {
    if (this.access !== 'public' && this.access !== 'private') {
      errors.push('Access must be "public" or "private"');
    }
  }
  else if(this.selectedTargetType === 'Person') {
    if (!this.role.trim()) {
      errors.push('Role must not be empty');
    }
  }    
  return errors;
}

checkDate(date: string){
  const parts = date.split('/'); 
  return new Date(parseInt(parts[2]), parseInt(parts[1])-1, parseInt(parts[0])); 
}

createPerson() {
  this.submitStatus = true;
  const errors = this.checkInputs();
  if( errors.length === 0){
    const dob = this.checkDate(this.dobEntry);
    const new_person = new Person(9999, this.targetName, this.altName, new Date(), 'New', new Date(dob), this.role);
    this.createTarget.postPerson(new_person).subscribe({
      next: (response) => console.log(response),
      error: (error) => console.error('Error:', error),});
    this.cdr.detectChanges();
    this.changeToView();
  }
  else
  {
    this.submitStatus = false;
    console.log(errors)
  }
}

createLocation() {
  this.submitStatus = true;
  const errors = this.checkInputs();
  if( errors.length === 0 ){
    const new_location = new Location(9999, this.targetName, this.altName, new Date(), 'New', this.access);
    console.log(new_location)
    this.createTarget.postLocation(new_location).subscribe({
      next: (response) => console.log(response),
      error: (error) => console.error('Error:', error),
    });
    this.cdr.detectChanges();
    this.changeToView();
  }
  else
  {
    this.submitStatus = false
    console.log(errors)
  }
}

changeToView(){
  this.router.navigate(['/targets/view'])
}

}
